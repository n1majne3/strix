"""Streaming parser for LiteLLM native tool-call events.

Provides a stateful accumulator that processes LiteLLM streaming chunk deltas
and produces ``StreamSegment`` objects for the TUI.  With native ``tools=``
calling, the model emits structured ``delta.tool_calls`` data rather than
in-line XML, so this module no longer performs any XML parsing.
"""

import json
import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal


logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public data structures
# ---------------------------------------------------------------------------


@dataclass
class StreamSegment:
    """A single piece of content from the streaming response.

    ``type="text"`` segments carry plain text the model outputs.
    ``type="tool"``  segments represent a tool call with its name, arguments
    (as they accumulate), and a completion flag.
    """

    type: Literal["text", "tool"]
    content: str
    tool_name: str | None = None
    args: dict[str, str] | None = None
    is_complete: bool = False


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

# Pre-compiled patterns for partial-JSON argument extraction
_RE_STRING_ARG = re.compile(r'"(\w+)"\s*:\s*"((?:[^"\\]|\\.)*)"')
_RE_LITERAL_ARG = re.compile(r'"(\w+)"\s*:\s*(\d+(?:\.\d+)?|true|false|null)')


def _flatten_args(d: Mapping[str, Any]) -> dict[str, str]:
    """Flatten a (possibly nested) dict to ``{str: str}`` for display."""
    out: dict[str, str] = {}
    for key, value in d.items():
        if isinstance(value, (dict, list)):
            out[key] = json.dumps(value, ensure_ascii=False)
        else:
            out[key] = str(value)
    return out


def _parse_partial_json_args(raw: str) -> dict[str, str]:
    """Extract key-value pairs from an incomplete JSON string.

    Handles the streaming case where ``arguments_json`` is still being built
    and is not yet valid JSON.  We look for ``"key": "value"`` patterns.
    """
    args: dict[str, str] = {}
    stripped = raw.strip()
    if not stripped:
        return args

    for m in _RE_STRING_ARG.finditer(stripped):
        args[m.group(1)] = m.group(2)

    for m in _RE_LITERAL_ARG.finditer(stripped):
        if m.group(1) not in args:
            args[m.group(1)] = m.group(2)

    return args


@dataclass
class _ToolCallState:
    """Accumulates a single tool call across many streaming chunks.

    LiteLLM sends tool-call data incrementally:
      - First chunk: sets ``id`` and ``function.name``
      - Subsequent chunks: append fragments to ``function.arguments``
    """

    id: str = ""
    name: str = ""
    arguments_json: str = ""
    is_complete: bool = False

    def update(self, tc_delta: Any) -> None:
        """Merge data from one ``delta.tool_calls[i]`` chunk."""
        tc_id = getattr(tc_delta, "id", None)
        if tc_id:
            self.id = tc_id

        func = getattr(tc_delta, "function", None)
        if func is None:
            return

        name = getattr(func, "name", None)
        if name:
            self.name = name

        arguments = getattr(func, "arguments", None)
        if arguments:
            self.arguments_json += arguments

    @property
    def parsed_args(self) -> dict[str, str]:
        """Best-effort extraction of arguments as ``{str: str}``."""
        if not self.arguments_json:
            return {}
        try:
            parsed = json.loads(self.arguments_json)
        except json.JSONDecodeError:
            return _parse_partial_json_args(self.arguments_json)

        if isinstance(parsed, dict):
            return _flatten_args(parsed)  # type: ignore[arg-type]
        return {"value": self.arguments_json}

    def to_segment(self) -> StreamSegment:
        """Convert current state to a ``StreamSegment``."""
        return StreamSegment(
            type="tool",
            content=self.arguments_json,
            tool_name=self.name or None,
            args=self.parsed_args if self.arguments_json else None,
            is_complete=self.is_complete,
        )


# ---------------------------------------------------------------------------
# Streaming accumulator
# ---------------------------------------------------------------------------


class StreamingAccumulator:
    """Stateful accumulator for LiteLLM streaming chunks.

    Usage::

        acc = StreamingAccumulator()
        async for chunk in response:
            delta = chunk.choices[0].delta
            acc.process_delta(delta)

            # Get current segments for TUI rendering
            segments = acc.get_segments()

        acc.mark_complete()
        final_segments = acc.get_segments()
    """

    def __init__(self) -> None:
        self.text_content: str = ""
        self._tool_calls: dict[int, _ToolCallState] = {}

    # -- mutation -----------------------------------------------------------

    def process_delta(self, delta: Any) -> None:
        """Process a streaming chunk's ``delta`` object.

        Parameters
        ----------
        delta:
            ``chunk.choices[0].delta`` from a LiteLLM streaming chunk.
            Expected attributes: ``.content`` (``str | None``) and
            ``.tool_calls`` (``list | None``).
        """
        text = getattr(delta, "content", None) or ""
        if text:
            self.text_content += text

        tool_calls = getattr(delta, "tool_calls", None)
        if tool_calls:
            for tc_delta in tool_calls:
                idx = getattr(tc_delta, "index", 0)
                if idx not in self._tool_calls:
                    self._tool_calls[idx] = _ToolCallState()
                self._tool_calls[idx].update(tc_delta)

    def process_text(self, text: str) -> None:
        """Accumulate raw text without any chunk structure.

        Useful when integrating with legacy paths that feed plain strings.
        """
        if text:
            self.text_content += text

    def mark_complete(self) -> None:
        """Mark all tracked tool calls as complete.

        Call this when the stream finishes (the model sends a
        ``finish_reason="tool_calls"`` or the stream ends).
        """
        for state in self._tool_calls.values():
            state.is_complete = True

    # -- query --------------------------------------------------------------

    def get_segments(self) -> list[StreamSegment]:
        """Return the current list of ``StreamSegment`` objects.

        Text is always first, followed by tool calls in index order.
        """
        segments: list[StreamSegment] = []

        text = self.text_content.strip()
        if text:
            segments.append(StreamSegment(type="text", content=text))

        segments.extend(
            self._tool_calls[idx].to_segment() for idx in sorted(self._tool_calls)
        )

        return segments

    @property
    def has_tool_calls(self) -> bool:
        """Whether any tool-call data has been received."""
        return bool(self._tool_calls)

    @property
    def has_content(self) -> bool:
        """Whether any content (text or tool calls) has been received."""
        return bool(self.text_content.strip()) or bool(self._tool_calls)

    def __repr__(self) -> str:
        return (
            f"StreamingAccumulator(text={len(self.text_content)} chars, "
            f"tool_calls={len(self._tool_calls)})"
        )


# ---------------------------------------------------------------------------
# Backward-compatible convenience function
# ---------------------------------------------------------------------------


def parse_streaming_content(content: str) -> list[StreamSegment]:
    """Parse *text-only* streaming content into segments.

    This is a simplified backward-compatible entry point.  With native
    ``tools=`` calling, tool calls arrive as structured ``delta.tool_calls``
    events, not as in-line text.  Use :class:`StreamingAccumulator` for the
    full streaming flow.

    Parameters
    ----------
    content:
        Accumulated text from streaming (plain prose, no XML tool tags).

    Returns
    -------
    list[StreamSegment]
        Typically a single text segment.  Returns an empty list for blank
        content.
    """
    if not content:
        return []

    text = content.strip()
    if text:
        return [StreamSegment(type="text", content=text)]
    return []

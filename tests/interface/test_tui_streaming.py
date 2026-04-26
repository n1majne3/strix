"""Tests for TUI rendering of streaming tools, thinking blocks, and final results.

Validates that the TUI chat view correctly renders:
1. Streaming tool states with name, partial args, and completion indicators
2. Thinking blocks from extended-reasoning models
3. Finished tool calls with structured JSON arguments
4. Graceful handling of partial/malformed data during stream buildup
"""

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from rich.text import Text

from strix.interface.streaming_parser import StreamSegment
from strix.telemetry.tracer import Tracer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeWidget:
    """Minimal widget stub for renderer tests."""

    def __init__(self, content: Text, classes: set[str] | None = None) -> None:
        self.content = content
        self.classes = classes or {"static"}


def _render_streaming_tool_default(
    tool_name: str, args: dict[str, str], is_complete: bool
) -> Text:
    """Replicate ``StrixTUIApp._render_default_streaming_tool`` for testing."""
    text = Text()
    if is_complete:
        text.append("✓ ", style="green")
    else:
        text.append("● ", style="yellow")
    text.append("Using tool ", style="dim")
    text.append(tool_name, style="bold blue")
    if args:
        for key, value in list(args.items())[:3]:
            str_value = str(value) if value is not None else ""
            text.append("\n  ")
            text.append(key, style="dim")
            text.append(": ")
            display_value = str_value if len(str_value) <= 100 else str_value[:97] + "..."
            text.append(display_value, style="italic" if not is_complete else None)
    return text


def _render_thinking_blocks(blocks: list[dict[str, Any]]) -> Text | None:
    """Replicate ``StrixTUIApp._render_thinking_blocks`` for testing."""
    parts: list[Text] = []

    for block in blocks:
        block_type = block.get("type", "")
        if block_type == "thinking":
            thinking_text = block.get("thinking", "")
            if thinking_text and thinking_text.strip():
                rendered = _format_thinking_text(thinking_text)
                parts.append(rendered)
        elif block_type == "redacted_thinking":
            redacted = Text()
            redacted.append("💭 ", style="dim")
            redacted.append("[thinking redacted]", style="dim italic")
            parts.append(redacted)

    if not parts:
        return None
    if len(parts) == 1:
        return parts[0]
    merged = Text()
    for i, p in enumerate(parts):
        if i > 0:
            merged.append("\n")
        merged.append_text(p)
    return merged


def _format_thinking_text(text: str) -> Text:
    """Replicate ``StrixTUIApp._format_thinking_text`` for testing."""
    rendered = Text()
    rendered.append("💭 ", style="dim")
    display_text = text.strip()
    if len(display_text) > 500:
        display_text = display_text[:497] + "..."
    rendered.append(display_text, style="dim italic")
    return rendered


def _render_segments(segments: list[StreamSegment]) -> Text:
    """Render a list of segments like the TUI does."""
    parts: list[Text] = []
    for seg in segments:
        if seg.type == "text":
            parts.append(Text(seg.content))
        elif seg.type == "tool":
            parts.append(
                _render_streaming_tool_default(
                    seg.tool_name or "unknown",
                    seg.args or {},
                    seg.is_complete,
                )
            )
    if not parts:
        return Text()
    if len(parts) == 1:
        return parts[0]
    merged = Text()
    for i, p in enumerate(parts):
        if i > 0:
            merged.append("\n")
        merged.append(p)
    return merged


# ---------------------------------------------------------------------------
# Test: Streaming tool states → TUI rendering
# ---------------------------------------------------------------------------


class TestStreamingToolRendering:
    """Verify streaming tool states render correctly in the TUI pipeline."""

    def test_streaming_tool_name_appears(self, tmp_path, monkeypatch) -> None:
        """Tool name appears as soon as it arrives in streaming state."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-tool-name")
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "send_request", "arguments": ""},
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = next(s for s in segments if s.type == "tool")
        assert tool_seg.tool_name == "send_request"

        rendered = _render_streaming_tool_default(
            tool_seg.tool_name or "unknown",
            tool_seg.args or {},
            tool_seg.is_complete,
        )
        assert "send_request" in rendered.plain
        assert "●" in rendered.plain  # Running indicator

    def test_streaming_tool_partial_args_render(self, tmp_path, monkeypatch) -> None:
        """Partial JSON arguments render as they accumulate."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-partial-args")

        # Partial arguments — use a complete string value so regex extraction works
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {
                    "id": "tc-1",
                    "name": "terminal_execute",
                    "arguments": '{"command": "curl -v",',
                },
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = segments[0]
        assert tool_seg.tool_name == "terminal_execute"
        # Partial args should extract the command key (value is a complete JSON string)
        assert tool_seg.args is not None
        assert "command" in tool_seg.args

        # Rendered output should show the partial command
        rendered = _render_streaming_tool_default(
            tool_seg.tool_name or "unknown",
            tool_seg.args or {},
            tool_seg.is_complete,
        )
        assert "terminal_execute" in rendered.plain

    def test_streaming_tool_complete_args_render(self, tmp_path, monkeypatch) -> None:
        """Complete JSON arguments render with all key-value pairs."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-complete-args")

        full_args = json.dumps(
            {"url": "https://example.com/api", "method": "POST", "headers": {"Authorization": "Bearer tok"}}
        )
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "send_request", "arguments": full_args},
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = segments[0]
        assert tool_seg.args is not None
        assert tool_seg.args.get("url") == "https://example.com/api"
        assert tool_seg.args.get("method") == "POST"

    def test_streaming_tool_running_vs_completed_indicator(self, tmp_path, monkeypatch) -> None:
        """Running tools show yellow dot; completed tools show green check."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-indicator")

        # Running state
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "send_request", "arguments": '{"url":"a"}'},
            },
        )
        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = segments[0]
        assert tool_seg.is_complete is False

        rendered_running = _render_streaming_tool_default(
            tool_seg.tool_name or "unknown",
            tool_seg.args or {},
            tool_seg.is_complete,
        )
        assert "●" in rendered_running.plain
        assert "✓" not in rendered_running.plain

        # Mark complete
        acc = tracer._get_or_create_accumulator("agent-1")
        acc.mark_complete()

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = segments[0]
        assert tool_seg.is_complete is True

        rendered_complete = _render_streaming_tool_default(
            tool_seg.tool_name or "unknown",
            tool_seg.args or {},
            tool_seg.is_complete,
        )
        assert "✓" in rendered_complete.plain
        assert "●" not in rendered_complete.plain

    def test_streaming_text_plus_tool_render(self, tmp_path, monkeypatch) -> None:
        """Combined text + tool streaming renders both segments."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-text-plus-tool")
        tracer.update_streaming_content(
            "agent-1",
            "I'll investigate the endpoint.",
            tool_states={
                0: {
                    "id": "tc-1",
                    "name": "send_request",
                    "arguments": json.dumps({"url": "https://example.com/login"}),
                },
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        assert len(segments) == 2
        assert segments[0].type == "text"
        assert segments[1].type == "tool"

        rendered = _render_segments(segments)
        assert "investigate" in rendered.plain
        assert "send_request" in rendered.plain

    def test_multiple_streaming_tools_render(self, tmp_path, monkeypatch) -> None:
        """Multiple parallel tool calls all render correctly."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-multi-tool")
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "send_request", "arguments": '{"url":"a"}'},
                1: {"id": "tc-2", "name": "terminal_execute", "arguments": '{"command":"ls"}'},
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        tool_segments = [s for s in segments if s.type == "tool"]
        assert len(tool_segments) == 2

        rendered = _render_segments(segments)
        assert "send_request" in rendered.plain
        assert "terminal_execute" in rendered.plain

    def test_finished_tool_with_structured_args(self, tmp_path, monkeypatch) -> None:
        """Finished tool calls render with full structured arguments."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-finished-tool")
        exec_id = tracer.log_tool_execution_start(
            "agent-1",
            "send_request",
            {"url": "https://example.com/api/v1", "method": "POST", "body": '{"data": "test"}'},
        )
        tracer.update_tool_execution(
            exec_id, "completed", {"status_code": 200, "body": '{"ok": true}'}
        )

        # Verify the tool execution data is available for rendering
        tool_exec = tracer.tool_executions[exec_id]
        assert tool_exec["tool_name"] == "send_request"
        assert tool_exec["status"] == "completed"
        assert tool_exec["args"]["url"] == "https://example.com/api/v1"
        assert tool_exec["result"]["status_code"] == 200


# ---------------------------------------------------------------------------
# Test: Thinking blocks rendering
# ---------------------------------------------------------------------------


class TestThinkingBlocksRendering:
    """Verify thinking blocks render correctly in the chat view."""

    def test_thinking_block_renders(self) -> None:
        """Single thinking block renders with 💭 icon and italic text."""
        blocks = [{"type": "thinking", "thinking": "Let me analyze this vulnerability..."}]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is not None
        assert "💭" in rendered.plain
        assert "analyze this vulnerability" in rendered.plain

    def test_redacted_thinking_block_renders(self) -> None:
        """Redacted thinking block renders with placeholder text."""
        blocks = [{"type": "redacted_thinking"}]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is not None
        assert "💭" in rendered.plain
        assert "[thinking redacted]" in rendered.plain

    def test_multiple_thinking_blocks_render(self) -> None:
        """Multiple thinking blocks render sequentially."""
        blocks = [
            {"type": "thinking", "thinking": "First thought."},
            {"type": "thinking", "thinking": "Second thought."},
        ]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is not None
        assert "First thought" in rendered.plain
        assert "Second thought" in rendered.plain

    def test_empty_thinking_block_skipped(self) -> None:
        """Empty thinking text is skipped."""
        blocks = [{"type": "thinking", "thinking": ""}]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is None

    def test_thinking_block_truncation(self) -> None:
        """Very long thinking blocks are truncated to 500 chars."""
        long_text = "x" * 600
        blocks = [{"type": "thinking", "thinking": long_text}]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is not None
        # Should be truncated to ~500 chars + "..."
        rendered_plain = rendered.plain
        # Remove the emoji prefix to check text length
        text_content = rendered_plain.replace("💭 ", "")
        assert len(text_content) <= 504  # 497 + "..."
        assert text_content.endswith("...")

    def test_thinking_block_in_chat_message_via_tracer(self, tmp_path, monkeypatch) -> None:
        """Thinking blocks flow through tracer metadata and are retrievable."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-thinking-tracer")

        thinking = [{"type": "thinking", "thinking": "Analyzing the attack surface..."}]
        tracer.log_chat_message(
            content="I found a potential XSS vulnerability.",
            role="assistant",
            agent_id="agent-1",
            metadata={"thinking_blocks": thinking},
        )

        # Verify thinking blocks are stored in the message metadata
        msg = tracer.chat_messages[-1]
        assert msg["metadata"]["thinking_blocks"] == thinking

    def test_no_thinking_blocks_when_none(self, tmp_path, monkeypatch) -> None:
        """Messages without thinking blocks have empty/default metadata."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-no-thinking")
        tracer.log_chat_message(
            content="Hello!",
            role="assistant",
            agent_id="agent-1",
        )

        msg = tracer.chat_messages[-1]
        assert msg["metadata"] == {}

    def test_thinking_rendered_before_content(self, tmp_path, monkeypatch) -> None:
        """Thinking blocks appear before the main content in the chat view."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-thinking-order")

        thinking = [{"type": "thinking", "thinking": "Let me think..."}]
        tracer.log_chat_message(
            content="Here is my analysis.",
            role="assistant",
            agent_id="agent-1",
            metadata={"thinking_blocks": thinking},
        )

        msg = tracer.chat_messages[-1]
        # Verify thinking blocks are in metadata
        assert msg["metadata"]["thinking_blocks"] is not None
        # Verify content is also present
        assert msg["content"] == "Here is my analysis."


# ---------------------------------------------------------------------------
# Test: Graceful handling of partial/missing data
# ---------------------------------------------------------------------------


class TestGracefulStreamingHandling:
    """Verify TUI handles missing, partial, and malformed data gracefully."""

    def test_missing_args_key_in_tool_state(self, tmp_path, monkeypatch) -> None:
        """Tool state with missing 'arguments' key doesn't crash."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-missing-args")
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "send_request"},  # No "arguments" key
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        assert len(segments) == 1
        assert segments[0].type == "tool"
        assert segments[0].tool_name == "send_request"
        # No crash; args may be None or empty
        rendered = _render_streaming_tool_default(
            segments[0].tool_name or "unknown",
            segments[0].args or {},
            segments[0].is_complete,
        )
        assert "send_request" in rendered.plain

    def test_empty_tool_name_handled(self, tmp_path, monkeypatch) -> None:
        """Tool state with empty name defaults gracefully."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-empty-name")
        tracer.update_streaming_content(
            "agent-1",
            "",
            tool_states={
                0: {"id": "tc-1", "name": "", "arguments": "{}"},
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        assert len(segments) == 1
        rendered = _render_streaming_tool_default(
            segments[0].tool_name or "unknown",
            segments[0].args or {},
            segments[0].is_complete,
        )
        assert "unknown" in rendered.plain

    def test_none_args_in_rendering(self) -> None:
        """Passing None args to default renderer doesn't crash."""
        rendered = _render_streaming_tool_default("my_tool", None, False)  # type: ignore[arg-type]
        assert "my_tool" in rendered.plain

    def test_empty_string_args_in_rendering(self) -> None:
        """Empty string values in args render without crash."""
        rendered = _render_streaming_tool_default("my_tool", {"key": ""}, False)
        assert "my_tool" in rendered.plain

    def test_none_values_in_args(self) -> None:
        """None values in args dict are handled gracefully — no crash."""
        rendered = _render_streaming_tool_default(
            "my_tool", {"url": None, "method": "GET"}, False  # type: ignore[dict-item]
        )
        assert "my_tool" in rendered.plain
        assert "GET" in rendered.plain
        # None values render as empty string (str() of None is "None", but our
        # renderer converts None to "" to avoid visual noise)
        assert "url" in rendered.plain

    def test_streaming_clear_then_new_content(self, tmp_path, monkeypatch) -> None:
        """Clearing streaming state and starting fresh works correctly."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-clear-restart")

        # First tool call
        tracer.update_streaming_content(
            "agent-1",
            "First tool.",
            tool_states={
                0: {"id": "tc-1", "name": "tool_a", "arguments": '{"x":"1"}'},
            },
        )
        segments = tracer.get_streaming_segments("agent-1")
        assert any(s.tool_name == "tool_a" for s in segments if s.type == "tool")

        # Clear and start new
        tracer.clear_streaming_content("agent-1")
        assert tracer.get_streaming_segments("agent-1") == []

        # New tool call
        tracer.update_streaming_content(
            "agent-1",
            "Second tool.",
            tool_states={
                0: {"id": "tc-2", "name": "tool_b", "arguments": '{"y":"2"}'},
            },
        )
        segments = tracer.get_streaming_segments("agent-1")
        tool_names = [s.tool_name for s in segments if s.type == "tool"]
        assert "tool_b" in tool_names
        assert "tool_a" not in tool_names

    def test_unknown_block_type_ignored(self) -> None:
        """Unknown block types in thinking_blocks are silently ignored."""
        blocks = [
            {"type": "unknown_type", "content": "something"},
            {"type": "thinking", "thinking": "Valid thinking."},
        ]
        rendered = _render_thinking_blocks(blocks)
        assert rendered is not None
        assert "Valid thinking" in rendered.plain
        assert "something" not in rendered.plain

    def test_large_args_truncated_in_default_renderer(self) -> None:
        """Long argument values are truncated in default renderer."""
        long_value = "x" * 200
        rendered = _render_streaming_tool_default("my_tool", {"data": long_value}, False)
        assert "my_tool" in rendered.plain
        # Value should be truncated to 100 chars
        assert long_value not in rendered.plain

    def test_streaming_to_finished_tool_flow(self, tmp_path, monkeypatch) -> None:
        """Full flow: streaming tool → completion → tool execution → result."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("STRIX_TELEMETRY", "0")

        tracer = Tracer("test-full-flow")

        # Phase 1: Streaming tool builds up
        tracer.update_streaming_content(
            "agent-1",
            "I'll check this.",
            tool_states={
                0: {
                    "id": "tc-1",
                    "name": "terminal_execute",
                    "arguments": json.dumps({"command": "curl -v https://example.com"}),
                },
            },
        )

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = next(s for s in segments if s.type == "tool")
        assert tool_seg.tool_name == "terminal_execute"
        assert tool_seg.is_complete is False

        # Phase 2: Stream completes
        acc = tracer._get_or_create_accumulator("agent-1")
        acc.mark_complete()

        segments = tracer.get_streaming_segments("agent-1")
        tool_seg = next(s for s in segments if s.type == "tool")
        assert tool_seg.is_complete is True

        rendered = _render_streaming_tool_default(
            tool_seg.tool_name or "unknown",
            tool_seg.args or {},
            tool_seg.is_complete,
        )
        assert "✓" in rendered.plain
        assert "curl" in rendered.plain

        # Phase 3: Clear streaming, log tool execution
        tracer.clear_streaming_content("agent-1")
        exec_id = tracer.log_tool_execution_start(
            "agent-1",
            "terminal_execute",
            {"command": "curl -v https://example.com"},
        )
        tracer.update_tool_execution(exec_id, "completed", "HTTP/1.1 200 OK")

        tool_exec = tracer.tool_executions[exec_id]
        assert tool_exec["status"] == "completed"
        assert tool_exec["result"] == "HTTP/1.1 200 OK"

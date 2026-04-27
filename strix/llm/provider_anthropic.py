"""Anthropic LLM provider backed by litellm."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import litellm
from litellm import acompletion, completion_cost, stream_chunk_builder, supports_reasoning
from litellm.utils import supports_prompt_caching, supports_vision

from strix.llm.config import LLMConfig
from strix.llm.provider_base import LLMResponse, ProviderBase, RequestStats

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# litellm global configuration — must execute before any litellm call
# ---------------------------------------------------------------------------
litellm.drop_params = True
litellm.modify_params = True
litellm._logging._disable_debugging()


class AnthropicProvider(ProviderBase):
    """Concrete provider that drives Anthropic models via litellm."""

    def __init__(self, config: LLMConfig, reasoning_effort: str) -> None:
        self._config = config
        self._reasoning_effort = reasoning_effort
        self._stats = RequestStats()

    # ------------------------------------------------------------------
    # ProviderBase abstract method implementations
    # ------------------------------------------------------------------

    async def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
        **kwargs: Any,
    ) -> AsyncIterator[LLMResponse]:
        accumulated = ""
        chunks: list[Any] = []
        done_streaming = 0

        # Track partial tool-call state during streaming so the TUI can
        # render tool calls forming in real-time.
        tool_call_states: dict[int, dict[str, str]] = {}
        has_tool_call_data = False

        self._stats.requests += 1

        args = self.build_completion_args(messages, tools, tool_choice)

        try:
            response = await acompletion(**args, stream=True)
        except Exception as e:
            # Handle LiteLLM errors during request setup
            logger.error("LiteLLM request failed: %s", e)
            raise

        # Wrap the entire streaming loop to catch malformed tool call errors
        # from models that don't properly support Anthropic-style tool calling
        try:
            async for chunk in response:
                chunks.append(chunk)
                if done_streaming:
                    done_streaming += 1
                    if getattr(chunk, "usage", None) or done_streaming > 5:
                        break
                    continue

                # Extract text delta
                text_delta = self._get_chunk_content(chunk)
                if text_delta:
                    accumulated += text_delta

                # Extract tool-call deltas from this chunk
                raw_delta = None
                if chunk.choices and hasattr(chunk.choices[0], "delta"):
                    raw_delta = chunk.choices[0].delta

                tc_deltas = getattr(raw_delta, "tool_calls", None) if raw_delta else None
                if tc_deltas:
                    has_tool_call_data = True
                    for tc in tc_deltas:
                        idx = getattr(tc, "index", 0)
                        if idx not in tool_call_states:
                            tool_call_states[idx] = {"id": "", "name": "", "arguments": ""}
                        state = tool_call_states[idx]
                        tc_id = getattr(tc, "id", None)
                        if tc_id:
                            state["id"] = tc_id
                        func = getattr(tc, "function", None)
                        if func is not None:
                            name = getattr(func, "name", None)
                            if name:
                                state["name"] = name
                            arguments = getattr(func, "arguments", None)
                            if arguments:
                                state["arguments"] += arguments

                # Yield intermediate response if there's new content or tool data
                if text_delta or tc_deltas:
                    yield LLMResponse(
                        content=accumulated,
                        streaming_tool_states=dict(tool_call_states) if has_tool_call_data else None,
                    )
        except Exception as e:
            # Catch malformed tool call errors from incompatible models
            error_msg = str(e)
            if "Failed to parse tool call arguments" in error_msg or "Unterminated string" in error_msg:
                logger.warning(
                    "Model returned malformed tool call arguments. "
                    "This usually indicates the model doesn't properly support Anthropic-style tool calling. "
                    "Error: %s",
                    error_msg[:500],
                )
                # Yield what we accumulated so far as text content
                if accumulated or tool_call_states:
                    # Try to salvage partial tool calls
                    tool_invocations = None
                    tool_calls_raw = None
                    if tool_call_states:
                        tool_invocations = []
                        tool_calls_raw = []
                        for idx, state in sorted(tool_call_states.items()):
                            if state["name"]:
                                # Try to parse arguments, fall back to empty if malformed
                                try:
                                    args_parsed = json.loads(state["arguments"]) if state["arguments"] else {}
                                except json.JSONDecodeError:
                                    logger.warning(
                                        "Could not parse arguments for tool %s: %s",
                                        state["name"],
                                        state["arguments"][:200],
                                    )
                                    args_parsed = {}
                                tool_invocations.append({
                                    "toolName": state["name"],
                                    "args": args_parsed,
                                    "id": state["id"] or f"salvaged_{idx}",
                                })
                                tool_calls_raw.append({
                                    "id": state["id"] or f"salvaged_{idx}",
                                    "type": "function",
                                    "function": {
                                        "name": state["name"],
                                        "arguments": state["arguments"],
                                    },
                                })
                    yield LLMResponse(
                        content=accumulated,
                        tool_invocations=tool_invocations,
                        tool_calls=tool_calls_raw,
                        thinking_blocks=None,
                    )
                    return
            # Re-raise other errors
            raise

        # Build the complete response from chunks for metadata extraction
        built_response = None
        if chunks:
            try:
                built_response = stream_chunk_builder(chunks)
                self._update_usage_stats(built_response)
            except Exception:  # noqa: BLE001
                logger.warning("Failed to build stream response for usage stats")

        # Extract native tool_calls from the response
        tool_calls_raw: list[dict[str, Any]] | None = None
        tool_invocations: list[dict[str, Any]] | None = None

        if built_response and built_response.choices:
            message = built_response.choices[0].message
            raw_tool_calls = getattr(message, "tool_calls", None)

            if raw_tool_calls:
                tool_calls_raw = []
                tool_invocations = []
                for tc in raw_tool_calls:
                    tc_dict = {
                        "id": tc.id,
                        "type": getattr(tc, "type", "function"),
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    tool_calls_raw.append(tc_dict)

                    # Parse arguments JSON string to typed args dict
                    try:
                        args_parsed = (
                            json.loads(tc.function.arguments) if tc.function.arguments else {}
                        )
                    except json.JSONDecodeError:
                        logger.warning(
                            "Failed to parse tool call arguments for %s: %s",
                            tc.function.name,
                            tc.function.arguments[:200],
                        )
                        args_parsed = {}

                    tool_invocations.append({
                        "toolName": tc.function.name,
                        "args": args_parsed,
                        "id": tc.id,
                    })

        # Use content from accumulated streaming text, or from the built response
        final_content = accumulated
        if not final_content and built_response and built_response.choices:
            msg_content = getattr(built_response.choices[0].message, "content", None)
            if msg_content:
                final_content = msg_content

        yield LLMResponse(
            content=final_content or "",
            tool_invocations=tool_invocations,
            tool_calls=tool_calls_raw,
            thinking_blocks=self._extract_thinking(chunks),
        )

    def supports_vision(self) -> bool:
        try:
            return bool(supports_vision(model=self._config.canonical_model))
        except Exception:  # noqa: BLE001
            return False

    def supports_reasoning(self) -> bool:
        try:
            return bool(supports_reasoning(model=self._config.canonical_model))
        except Exception:  # noqa: BLE001
            return False

    def supports_prompt_caching(self) -> bool:
        try:
            return bool(supports_prompt_caching(self._config.canonical_model))
        except Exception:  # noqa: BLE001
            return False

    def get_stats(self) -> RequestStats:
        return self._stats

    def get_model_name(self) -> str:
        return self._config.canonical_model

    # ------------------------------------------------------------------
    # Anthropic-specific helpers (public for testability)
    # ------------------------------------------------------------------

    def build_completion_args(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
    ) -> dict[str, Any]:
        """Build the litellm ``acompletion`` keyword arguments."""
        if not self.supports_vision():
            messages = self._strip_images(messages)

        args: dict[str, Any] = {
            "model": self._config.litellm_model,
            "messages": messages,
            "timeout": self._config.timeout,
            "stream_options": {"include_usage": True},
            "tools": tools,
            "tool_choice": tool_choice,
        }

        if self._config.api_key:
            args["api_key"] = self._config.api_key
        if self._config.api_base:
            args["api_base"] = self._config.api_base
        if self.supports_reasoning():
            args["reasoning_effort"] = self._reasoning_effort

        return args

    def should_retry(self, exc: Exception) -> bool:
        """Return True if *exc* is retryable (rate-limit, server error, etc.)."""
        code = getattr(exc, "status_code", None) or getattr(
            getattr(exc, "response", None), "status_code", None
        )
        return code is None or litellm._should_retry(code)

    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Anthropic-specific message preprocessing (prompt caching)."""
        if not messages or not self.supports_prompt_caching():
            return messages

        result = list(messages)

        if result[0].get("role") == "system":
            content = result[0]["content"]
            result[0] = {
                **result[0],
                "content": [
                    {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                ]
                if isinstance(content, str)
                else content,
            }
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_chunk_content(self, chunk: Any) -> str:
        if chunk.choices and hasattr(chunk.choices[0], "delta"):
            return getattr(chunk.choices[0].delta, "content", "") or ""
        return ""

    def _extract_thinking(self, chunks: list[Any]) -> list[dict[str, Any]] | None:
        if not chunks or not self.supports_reasoning():
            return None
        try:
            resp = stream_chunk_builder(chunks)
            if resp.choices and hasattr(resp.choices[0].message, "thinking_blocks"):
                blocks: list[dict[str, Any]] = resp.choices[0].message.thinking_blocks
                return blocks
        except Exception:  # noqa: BLE001, S110  # nosec B110
            pass
        return None

    def _update_usage_stats(self, response: Any) -> None:
        try:
            if hasattr(response, "usage") and response.usage:
                input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(response.usage, "completion_tokens", 0) or 0

                cached_tokens = 0
                if hasattr(response.usage, "prompt_tokens_details"):
                    prompt_details = response.usage.prompt_tokens_details
                    if hasattr(prompt_details, "cached_tokens"):
                        cached_tokens = prompt_details.cached_tokens or 0

                cost = self._extract_cost(response)
            else:
                input_tokens = 0
                output_tokens = 0
                cached_tokens = 0
                cost = 0.0

            self._stats.input_tokens += input_tokens
            self._stats.output_tokens += output_tokens
            self._stats.cached_tokens += cached_tokens
            self._stats.cost += cost

        except Exception:  # noqa: BLE001, S110  # nosec B110
            pass

    def _extract_cost(self, response: Any) -> float:
        if hasattr(response, "usage") and response.usage:
            direct_cost = getattr(response.usage, "cost", None)
            if direct_cost is not None:
                return float(direct_cost)
        try:
            if hasattr(response, "_hidden_params"):
                response._hidden_params.pop("custom_llm_provider", None)
            return completion_cost(response, model=self._config.canonical_model) or 0.0
        except Exception:  # noqa: BLE001
            return 0.0

    def _strip_images(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif isinstance(item, dict) and item.get("type") == "image_url":
                        text_parts.append("[Image removed - model doesn't support vision]")
                result.append({**msg, "content": "\n".join(text_parts)})
            else:
                result.append(msg)
        return result

"""Anthropic LLM provider backed by the native ``anthropic`` Python SDK."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

from anthropic import AsyncAnthropic

from strix.llm.provider_base import (
    LLMResponse,
    ProviderBase,
    RequestStats,
)


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from strix.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model-name heuristics for capability detection
# ---------------------------------------------------------------------------

_REASONING_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet",
    "claude-3-7-sonnet",
    "claude-4-sonnet",
    "claude-4-opus",
})

_VISION_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet",
    "claude-3-7-sonnet",
    "claude-4-sonnet",
    "claude-4-opus",
})

# ---------------------------------------------------------------------------
# Fallback pricing table (cost per token) for models not yet in litellm
# ---------------------------------------------------------------------------

_FALLBACK_PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-4": (3e-6, 1.5e-5),
    "claude-opus-4": (1.5e-5, 7.5e-5),
    "claude-3-5-sonnet": (3e-6, 1.5e-5),
    "claude-3-7-sonnet": (3e-6, 1.5e-5),
}

# HTTP status codes that are retryable
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503})

# Regex matching characters that are NOT valid in Anthropic tool call IDs
_TOOL_CALL_ID_INVALID_RE = re.compile(r"[^a-zA-Z0-9_-]")

# Thinking budgets mapped from effort levels
_THINKING_BUDGETS: dict[str, int] = {
    "low": 4096,
    "medium": 16384,
    "high": 65536,
}

_DEFAULT_MAX_TOKENS = 16384


class AnthropicProvider(ProviderBase):
    """Concrete provider that drives Anthropic models via the native SDK."""

    def __init__(self, config: LLMConfig, reasoning_effort: str) -> None:
        self._config = config
        self._reasoning_effort = reasoning_effort
        self._stats = RequestStats()
        self._model_name = self._strip_anthropic_prefix(config.litellm_model)
        self._client = AsyncAnthropic(
            api_key=config.api_key or None,
            base_url=config.api_base or None,
        )

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
        raise NotImplementedError("Streaming implemented in Task 5")

    def supports_vision(self) -> bool:
        """Use model-name heuristics to detect vision capability."""
        base = self._model_name
        return any(base == model or base.startswith(model + "-") for model in _VISION_MODELS)

    def supports_reasoning(self) -> bool:
        """Use model-name heuristics to detect reasoning capability."""
        base = self._model_name
        return any(base == model or base.startswith(model + "-") for model in _REASONING_MODELS)

    def supports_prompt_caching(self) -> bool:
        """Anthropic supports prompt caching for all current models."""
        return True

    def get_stats(self) -> RequestStats:
        return self._stats

    def get_model_name(self) -> str:
        return self._model_name

    # ------------------------------------------------------------------
    # Anthropic-specific helpers (public for testability)
    # ------------------------------------------------------------------

    def should_retry(self, exc: Exception) -> bool:
        """Return True if *exc* is retryable (rate-limit, server error)."""
        status_code = getattr(exc, "status_code", None)
        if status_code is None:
            # Connection errors, timeouts etc. are generally retryable
            return True
        return status_code in _RETRYABLE_STATUS_CODES

    def build_completion_args(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
    ) -> dict[str, Any]:
        """Build the ``AsyncAnthropic.messages.create`` keyword arguments."""
        if not self.supports_vision():
            messages = self._strip_images(messages)

        system, converted_messages = self._convert_messages(messages)
        converted_tools = self._convert_tools(tools) if tools else []

        args: dict[str, Any] = {
            "model": self._model_name,
            "messages": converted_messages,
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "timeout": self._config.timeout,
        }

        if system:
            args["system"] = system

        if converted_tools:
            args["tools"] = converted_tools
            args["tool_choice"] = self._convert_tool_choice(tool_choice)

        if self.supports_reasoning():
            budget = _THINKING_BUDGETS.get(self._reasoning_effort, _THINKING_BUDGETS["high"])
            args["thinking"] = {"type": "enabled", "budget_tokens": budget}

        return args

    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Add cache_control markers to system message for Anthropic prompt caching."""
        if not messages:
            return messages

        result = list(messages)

        if result[0].get("role") == "system":
            content = result[0]["content"]
            if isinstance(content, str):
                result[0] = {
                    **result[0],
                    "content": [
                        {
                            "type": "text",
                            "text": content,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                }

        return result

    # ------------------------------------------------------------------
    # Message conversion helpers
    # ------------------------------------------------------------------

    def _convert_messages(
        self,
        messages: list[dict[str, Any]],
    ) -> tuple[str | list[dict] | None, list[dict[str, Any]]]:
        """Convert OpenAI-style messages to Anthropic Messages API format.

        Returns:
            A tuple of (system_content, converted_messages) where system_content
            is a string extracted from system messages, or None if there are
            no system messages.
        """
        system_parts: list[str] = []
        converted: list[dict[str, Any]] = []

        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content")

            if role == "system":
                self._extract_system_content(content, system_parts)
            elif role == "assistant":
                converted.append(self._convert_assistant_message(msg))
            elif role == "tool":
                converted.append(self._convert_tool_result(msg))
            elif role == "user":
                converted.append({"role": "user", "content": content or ""})

        # Merge consecutive tool-result user messages into single user messages
        merged = self._merge_consecutive_user_messages(converted)

        # Build system content
        if not system_parts:
            system_content = None
        elif len(system_parts) == 1:
            system_content = system_parts[0]
        else:
            system_content = "\n\n".join(system_parts)

        return system_content, merged

    @staticmethod
    def _extract_system_content(
        content: Any,
        system_parts: list[str],
    ) -> None:
        """Extract text from a system message content into system_parts."""
        if isinstance(content, str):
            system_parts.append(content)
        elif isinstance(content, list):
            system_parts.extend(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )

    def _convert_assistant_message(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Convert an assistant message, handling tool_calls."""
        tool_calls = msg.get("tool_calls")
        content = msg.get("content")

        if not tool_calls:
            return {"role": "assistant", "content": content or ""}

        content_blocks: list[dict[str, Any]] = []
        # Add text content if present
        if content and isinstance(content, str) and content.strip():
            content_blocks.append({"type": "text", "text": content})
        # Add tool_use blocks
        for tc in tool_calls:
            tc_id = self._sanitize_tool_call_id(tc.get("id", f"gen_{id(tc)}"))
            func = tc.get("function", {})
            name = func.get("name", "")
            # Parse arguments JSON string to dict
            raw_args = func.get("arguments", "{}")
            try:
                input_dict = json.loads(raw_args) if raw_args else {}
            except (json.JSONDecodeError, TypeError):
                input_dict = {}
            content_blocks.append({
                "type": "tool_use",
                "id": tc_id,
                "name": name,
                "input": input_dict,
            })
        return {"role": "assistant", "content": content_blocks}

    def _convert_tool_result(self, msg: dict[str, Any]) -> dict[str, Any]:
        """Convert a tool result message to Anthropic format."""
        content = msg.get("content")
        tool_call_id = self._sanitize_tool_call_id(
            msg.get("tool_call_id", f"gen_{id(msg)}")
        )
        tool_content = content if isinstance(content, str) else json.dumps(content)
        return {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_call_id,
                    "content": tool_content,
                }
            ],
        }

    @staticmethod
    def _merge_consecutive_user_messages(
        messages: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Merge consecutive user messages into single user messages.

        Anthropic requires alternating user/assistant turns. Consecutive tool
        results (converted to user messages) must be merged.
        """
        merged: list[dict[str, Any]] = []
        for msg in messages:
            if (
                msg["role"] == "user"
                and isinstance(msg.get("content"), list)
                and merged
                and merged[-1]["role"] == "user"
                and isinstance(merged[-1].get("content"), list)
            ):
                # Merge content blocks
                merged[-1]["content"] = merged[-1]["content"] + msg["content"]
            else:
                merged.append(msg)
        return merged

    @staticmethod
    def _convert_tools(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI-style tool definitions to Anthropic format.

        OpenAI: {"type": "function", "function": {"name": ..., "parameters": ...}}
        Anthropic: {"name": ..., "input_schema": ...}
        """
        return [
            {
                "name": tool.get("function", {}).get("name", ""),
                "input_schema": tool.get("function", {}).get("parameters", {}),
            }
            for tool in tools
        ]

    @staticmethod
    def _convert_tool_choice(tool_choice: str) -> dict[str, str]:
        """Convert OpenAI-style tool_choice string to Anthropic format."""
        mapping = {
            "auto": {"type": "auto"},
            "none": {"type": "none"},
            "required": {"type": "any"},
        }
        return mapping.get(tool_choice, {"type": "auto"})

    # ------------------------------------------------------------------
    # Cost calculation helpers
    # ------------------------------------------------------------------

    def _extract_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> float:
        """Compute cost from token counts using litellm pricing data.

        Looks up per-token pricing from ``litellm.model_cost`` and falls back
        to a static pricing table for models not yet indexed by litellm.
        Returns 0.0 if pricing data is unavailable.
        """
        in_cost: float | None = None
        out_cost: float | None = None
        cache_cost: float | None = None

        # Try litellm's model_cost database first
        in_cost, out_cost, cache_cost = self._lookup_litellm_pricing(model)

        # Fall back to static pricing table
        if in_cost is None or out_cost is None:
            fallback = _FALLBACK_PRICING.get(model)
            if fallback is not None:
                in_cost, out_cost = fallback
                cache_cost = cache_cost or (in_cost * 0.1)

        if in_cost is None or out_cost is None:
            return 0.0

        # Compute: bill input minus cached at full rate, cached at cache rate
        effective_cached = cached_tokens or cache_read_tokens
        non_cached = max(input_tokens - effective_cached, 0)
        total = non_cached * in_cost + output_tokens * out_cost
        if effective_cached > 0 and cache_cost is not None:
            total += effective_cached * cache_cost
        elif effective_cached > 0:
            total += effective_cached * in_cost * 0.1

        return total

    @staticmethod
    def _lookup_litellm_pricing(
        model: str,
    ) -> tuple[float | None, float | None, float | None]:
        """Try to look up per-token pricing from litellm.model_cost.

        Returns (in_cost, out_cost, cache_cost) or (None, None, None)
        if unavailable.
        """
        try:
            import litellm  # noqa: PLC0415

            pricing = litellm.model_cost.get(model)
            if pricing is not None:
                return (
                    pricing.get("input_cost_per_token"),
                    pricing.get("output_cost_per_token"),
                    pricing.get("cache_read_input_token_cost"),
                )
        except Exception:  # noqa: BLE001
            logger.debug("litellm pricing lookup failed for %s", model)
        return None, None, None

    def _update_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        cache_creation_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> None:
        """Update accumulated usage statistics from token counts."""
        cached_tokens = cache_creation_tokens + cache_read_tokens
        cost = self._extract_cost(
            model=self._model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cache_read_tokens=cache_read_tokens,
        )

        self._stats.input_tokens += input_tokens
        self._stats.output_tokens += output_tokens
        self._stats.cached_tokens += cached_tokens
        self._stats.cost += cost

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_anthropic_prefix(model: str) -> str:
        """Strip ``anthropic/`` prefix from litellm-style model identifiers."""
        if model.startswith("anthropic/"):
            return model[len("anthropic/"):]
        return model

    @staticmethod
    def _strip_images(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove image content blocks from messages for non-vision models."""
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

    @staticmethod
    def _sanitize_tool_call_id(tc_id: str) -> str:
        """Sanitize a tool call ID to match Anthropic's requirements.

        Anthropic requires tool call IDs to match ``^[a-zA-Z0-9_-]+$`` and
        be at most 64 characters.
        """
        sanitized = _TOOL_CALL_ID_INVALID_RE.sub("_", tc_id)
        return sanitized[:64]

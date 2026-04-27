"""OpenAI LLM provider backed by the native ``openai`` Python SDK."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

from openai import APIStatusError, AsyncOpenAI

from strix.llm.provider_base import (
    LLMRequestFailedError,
    LLMResponse,
    ProviderBase,
    RequestStats,
)


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from strix.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Fallback pricing table (cost per token) for models not yet in litellm
# ---------------------------------------------------------------------------

_FALLBACK_PRICING: dict[str, tuple[float, float]] = {
    # model_name: (input_cost_per_token, output_cost_per_token)
    "gpt-4o": (2.5e-6, 1.0e-5),
    "gpt-4o-mini": (1.5e-7, 6.0e-7),
    "gpt-5": (1.25e-6, 1.0e-5),
    "gpt-5.1": (1.25e-6, 1.0e-5),
    "gpt-5.2": (1.75e-6, 1.4e-5),
    "gpt-5.4": (2.5e-6, 1.5e-5),
}

# ---------------------------------------------------------------------------
# Model-name heuristics for capability detection
# ---------------------------------------------------------------------------

_VISION_MODELS: frozenset[str] = frozenset({
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-5",
    "gpt-5.1",
    "gpt-5.2",
    "gpt-5.4",
})

# HTTP status codes that are retryable
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503})


class OpenAIProvider(ProviderBase):
    """Concrete provider that drives OpenAI models via the native SDK."""

    def __init__(self, config: LLMConfig, reasoning_effort: str) -> None:
        self._config = config
        self._reasoning_effort = reasoning_effort
        self._stats = RequestStats()
        self._model_name = self._strip_openai_prefix(config.litellm_model)
        self._client = AsyncOpenAI(
            api_key=config.api_key or None,
            base_url=config.api_base or None,
        )

    # ------------------------------------------------------------------
    # ProviderBase abstract method implementations
    # ------------------------------------------------------------------

    async def generate_stream(  # noqa: PLR0912, PLR0915
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
        **kwargs: Any,  # noqa: ARG002
    ) -> AsyncIterator[LLMResponse]:
        accumulated = ""
        tool_call_states: dict[int, dict[str, str]] = {}
        has_tool_call_data = False

        self._stats.requests += 1

        args = self._build_completion_args(messages, tools, tool_choice)

        try:
            response = await self._client.chat.completions.create(**args)
        except APIStatusError as exc:
            if self.should_retry(exc):
                raise
            raise LLMRequestFailedError(
                f"OpenAI request failed: {exc.message}",
                details=f"status={exc.status_code} body={exc.response.text[:500]}",
            ) from exc

        async for chunk in response:
            # When choices is empty but usage is present, we've reached the
            # final chunk carrying usage metadata — extract it and break.
            if not chunk.choices:
                if chunk.usage:
                    self._update_usage(chunk.usage)
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            # Extract text delta
            text_delta = getattr(delta, "content", None) or ""
            if text_delta:
                accumulated += text_delta

            # Extract tool-call deltas
            tc_deltas = getattr(delta, "tool_calls", None)
            if tc_deltas:
                has_tool_call_data = True
                for tc in tc_deltas:
                    idx = getattr(tc, "index", 0)
                    if idx not in tool_call_states:
                        tool_call_states[idx] = {"id": "", "name": "", "arguments": ""}
                    state = tool_call_states[idx]
                    # tool-call id only appears on the first delta for this index
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

        # After loop: build final LLMResponse with complete tool state
        tool_calls_raw: list[dict[str, Any]] | None = None
        tool_invocations: list[dict[str, Any]] | None = None

        if tool_call_states:
            tool_calls_raw = []
            tool_invocations = []
            for _idx, state in sorted(tool_call_states.items()):
                tc_dict = {
                    "id": state["id"],
                    "type": "function",
                    "function": {
                        "name": state["name"],
                        "arguments": state["arguments"],
                    },
                }
                tool_calls_raw.append(tc_dict)

                # Parse arguments JSON string to typed args dict
                try:
                    args_parsed = json.loads(state["arguments"]) if state["arguments"] else {}
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse tool call arguments for %s: %s",
                        state["name"],
                        state["arguments"][:200],
                    )
                    args_parsed = {}

                tool_invocations.append({
                    "toolName": state["name"],
                    "args": args_parsed,
                    "id": state["id"],
                })

        yield LLMResponse(
            content=accumulated or "",
            tool_invocations=tool_invocations,
            tool_calls=tool_calls_raw,
            thinking_blocks=None,
        )

    def supports_vision(self) -> bool:
        """Use model-name heuristics to detect vision capability."""
        base = self._model_name
        return any(base == model or base.startswith(model + "-") for model in _VISION_MODELS)

    def supports_reasoning(self) -> bool:
        """OpenAI reasoning models (o-series) are not yet supported in this provider."""
        return False

    def supports_prompt_caching(self) -> bool:
        """Prompt caching not yet implemented for the OpenAI provider."""
        return False

    def get_stats(self) -> RequestStats:
        return self._stats

    def get_model_name(self) -> str:
        return self._model_name

    # ------------------------------------------------------------------
    # OpenAI-specific helpers (public for testability)
    # ------------------------------------------------------------------

    def should_retry(self, exc: Exception) -> bool:
        """Return True if *exc* is retryable (rate-limit, server error)."""
        status_code = getattr(exc, "status_code", None)
        if status_code is None:
            # Connection errors, timeouts etc. are generally retryable
            return True
        return status_code in _RETRYABLE_STATUS_CODES

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_completion_args(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
    ) -> dict[str, Any]:
        """Build the ``AsyncOpenAI.chat.completions.create`` keyword arguments."""
        if not self.supports_vision():
            messages = self._strip_images(messages)

        args: dict[str, Any] = {
            "model": self._model_name,
            "messages": messages,
            "stream": True,
            "stream_options": {"include_usage": True},
            "timeout": self._config.timeout,
        }

        if tools:
            args["tools"] = tools
            args["tool_choice"] = tool_choice

        return args

    def _extract_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
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
        try:
            import litellm

            pricing = litellm.model_cost.get(model)
            if pricing is not None:
                in_cost = pricing.get("input_cost_per_token")
                out_cost = pricing.get("output_cost_per_token")
                cache_cost = pricing.get("cache_read_input_token_cost")
        except Exception:  # noqa: BLE001
            pass

        # Fall back to static pricing table
        if in_cost is None or out_cost is None:
            fallback = _FALLBACK_PRICING.get(model)
            if fallback is not None:
                in_cost, out_cost = fallback
                cache_cost = cache_cost or (in_cost * 0.1)  # 90% cache discount

        if in_cost is None or out_cost is None:
            return 0.0

        # Compute: bill input minus cached at full rate, cached at cache rate
        non_cached = max(input_tokens - cached_tokens, 0)
        total = non_cached * in_cost + output_tokens * out_cost
        if cached_tokens > 0 and cache_cost is not None:
            total += cached_tokens * cache_cost
        elif cached_tokens > 0:
            # Default: cached tokens at 10% of input cost
            total += cached_tokens * in_cost * 0.1

        return total

    def _update_usage(self, usage: Any) -> None:
        """Extract usage stats from the final streaming chunk."""
        try:
            input_tokens = getattr(usage, "prompt_tokens", 0) or 0
            output_tokens = getattr(usage, "completion_tokens", 0) or 0

            cached_tokens = 0
            prompt_details = getattr(usage, "prompt_tokens_details", None)
            if prompt_details and hasattr(prompt_details, "cached_tokens"):
                cached_tokens = prompt_details.cached_tokens or 0

            cost = self._extract_cost(
                model=self._model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cached_tokens=cached_tokens,
            )

            self._stats.input_tokens += input_tokens
            self._stats.output_tokens += output_tokens
            self._stats.cached_tokens += cached_tokens
            self._stats.cost += cost
        except Exception:  # noqa: BLE001
            logger.warning("Failed to extract usage stats from streaming chunk")

    @staticmethod
    def _strip_openai_prefix(model: str) -> str:
        """Strip ``openai/`` prefix from litellm-style model identifiers."""
        if model.startswith("openai/"):
            return model[len("openai/"):]
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

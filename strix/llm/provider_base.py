"""Abstract base class for LLM providers and shared data types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


class LLMRequestFailedError(Exception):
    """Raised when an LLM request fails after exhausting retries."""

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


@dataclass
class LLMResponse:
    """A single response chunk from an LLM provider."""

    content: str
    tool_invocations: list[dict[str, Any]] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    thinking_blocks: list[dict[str, Any]] | None = None
    # Partial tool-call state during streaming.  Maps tool-call index →
    # ``{"id": str, "name": str, "arguments": str}`` where *arguments* is
    # the raw accumulated JSON fragment.  ``None`` when no tool-call data
    # has been seen yet on this response.
    streaming_tool_states: dict[int, dict[str, str]] | None = None


@dataclass
class RequestStats:
    """Accumulated request usage statistics."""

    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost: float = 0.0
    requests: int = 0

    def to_dict(self) -> dict[str, int | float]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "cost": round(self.cost, 4),
            "requests": self.requests,
        }


class ProviderBase(ABC):
    """Abstract interface for streaming LLM providers.

    Concrete providers (Anthropic, OpenAI, etc.) must implement all abstract
    methods.  The LLM orchestration layer delegates streaming to a provider
    instance while retaining responsibility for system prompts, skills,
    retry logic, and conversation history preparation.
    """

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
        **kwargs: Any,
    ) -> AsyncIterator[LLMResponse]:
        """Stream LLM responses for the given messages.

        Args:
            messages: Conversation messages in provider-compatible format.
            tools: Tool definitions in provider-compatible format.
            tool_choice: Tool choice mode (e.g. "auto", "none", "required").
            **kwargs: Provider-specific options (reasoning_effort,
                stream_options, etc.).

        Yields:
            LLMResponse chunks as they arrive from the provider.
        """

    @abstractmethod
    def supports_vision(self) -> bool:
        """Return True if the underlying model supports image inputs."""

    @abstractmethod
    def supports_reasoning(self) -> bool:
        """Return True if the underlying model supports extended reasoning."""

    @abstractmethod
    def supports_prompt_caching(self) -> bool:
        """Return True if the provider supports prompt caching."""

    @abstractmethod
    def get_stats(self) -> RequestStats:
        """Return accumulated usage statistics for this provider."""

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model identifier used by this provider."""

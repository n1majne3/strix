"""Real API integration tests for Anthropic and OpenAI providers.

Makes actual streaming API calls through both providers, proving the full
round-trip works: streaming response, tool-call extraction, usage stats,
and cost tracking.

Tests are gated behind ``STRIX_ANTHROPIC_API_KEY`` and
``STRIX_OPENAI_API_KEY`` environment variables — they skip automatically
when the corresponding key is absent.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock

import pytest

from strix.llm.config import LLMConfig
from strix.llm.provider_anthropic import AnthropicProvider
from strix.llm.provider_openai import OpenAIProvider


# ---------------------------------------------------------------------------
# Environment key helpers
# ---------------------------------------------------------------------------

ANTHROPIC_KEY_ENV = "STRIX_ANTHROPIC_API_KEY"
OPENAI_KEY_ENV = "STRIX_OPENAI_API_KEY"

anthropic_key = os.environ.get(ANTHROPIC_KEY_ENV)
openai_key = os.environ.get(OPENAI_KEY_ENV)


# ---------------------------------------------------------------------------
# Provider factory helpers (real keys, mocked config objects)
# ---------------------------------------------------------------------------


def _make_anthropic_provider(
    api_key: str,
    model: str = "anthropic/claude-sonnet-4-20250514",
) -> AnthropicProvider:
    """Create a real AnthropicProvider with the given API key."""
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = model
    cfg.litellm_model = model
    cfg.timeout = 60
    cfg.api_key = api_key
    cfg.api_base = None
    cfg.enable_prompt_caching = False
    return AnthropicProvider(cfg, reasoning_effort="high")


def _make_openai_provider(
    api_key: str,
    model: str = "openai/gpt-4o-mini",
) -> OpenAIProvider:
    """Create a real OpenAIProvider with the given API key."""
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = model
    cfg.litellm_model = model
    cfg.timeout = 60
    cfg.api_key = api_key
    cfg.api_base = None
    return OpenAIProvider(cfg, reasoning_effort="high")


# ---------------------------------------------------------------------------
# Shared tool / message fixtures
# ---------------------------------------------------------------------------

WEATHER_TOOL: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                },
                "required": ["city"],
            },
        },
    }
]


# ===========================================================================
# Anthropic provider real API tests
# ===========================================================================


@pytest.mark.skipif(not anthropic_key, reason=f"{ANTHROPIC_KEY_ENV} not set")
class TestAnthropicRealAPI:
    """Real streaming API calls through the Anthropic provider."""

    async def test_streaming_text_response(self):
        """Simple streaming text completion returns content."""
        provider = _make_anthropic_provider(anthropic_key)
        messages = [{"role": "user", "content": "Say 'hello world' and nothing else."}]

        chunks: list[str] = []
        final_content = ""
        async for resp in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            if resp.content:
                final_content = resp.content
            chunks.append(resp)

        assert len(chunks) >= 1, "Should yield at least one response"
        assert "hello" in final_content.lower(), f"Expected 'hello' in response, got: {final_content!r}"

    async def test_streaming_tool_call_round_trip(self):
        """Model calls the weather tool and we can extract tool invocations."""
        provider = _make_anthropic_provider(anthropic_key)
        messages = [
            {"role": "user", "content": "What is the weather in San Francisco? Use the get_weather tool."},
        ]

        final = None
        async for resp in provider.generate_stream(
            messages, tools=WEATHER_TOOL, tool_choice="auto"
        ):
            final = resp

        assert final is not None
        assert final.tool_invocations is not None, "Expected tool invocations"
        assert len(final.tool_invocations) >= 1, "Expected at least one tool call"
        inv = final.tool_invocations[0]
        assert inv["toolName"] == "get_weather", f"Expected 'get_weather', got {inv['toolName']!r}"
        assert "city" in inv["args"], f"Expected 'city' in args, got {inv['args']!r}"
        assert inv["id"], "Tool call should have a non-empty id"

    async def test_usage_stats_populated(self):
        """After a real call, input_tokens and output_tokens are > 0."""
        provider = _make_anthropic_provider(anthropic_key)
        messages = [{"role": "user", "content": "Say 'test' and nothing else."}]

        async for _ in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            pass

        stats = provider.get_stats()
        assert stats.input_tokens > 0, f"input_tokens should be > 0, got {stats.input_tokens}"
        assert stats.output_tokens > 0, f"output_tokens should be > 0, got {stats.output_tokens}"
        assert stats.requests == 1, f"requests should be 1, got {stats.requests}"

    async def test_cost_is_nonzero(self):
        """After a real call, cost is > 0 (proves cost tracking works end-to-end)."""
        provider = _make_anthropic_provider(anthropic_key)
        messages = [{"role": "user", "content": "Say 'test' and nothing else."}]

        async for _ in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            pass

        stats = provider.get_stats()
        assert stats.cost > 0, f"cost should be > 0, got {stats.cost}"


# ===========================================================================
# OpenAI provider real API tests
# ===========================================================================


@pytest.mark.skipif(not openai_key, reason=f"{OPENAI_KEY_ENV} not set")
class TestOpenAIRealAPI:
    """Real streaming API calls through the OpenAI provider."""

    async def test_streaming_text_response(self):
        """Simple streaming text completion returns content."""
        provider = _make_openai_provider(openai_key)
        messages = [{"role": "user", "content": "Say 'hello world' and nothing else."}]

        chunks: list[str] = []
        final_content = ""
        async for resp in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            if resp.content:
                final_content = resp.content
            chunks.append(resp)

        assert len(chunks) >= 1, "Should yield at least one response"
        assert "hello" in final_content.lower(), f"Expected 'hello' in response, got: {final_content!r}"

    async def test_streaming_tool_call_round_trip(self):
        """Model calls the weather tool and we can extract tool invocations."""
        provider = _make_openai_provider(openai_key)
        messages = [
            {"role": "user", "content": "What is the weather in San Francisco? Use the get_weather tool."},
        ]

        final = None
        async for resp in provider.generate_stream(
            messages, tools=WEATHER_TOOL, tool_choice="auto"
        ):
            final = resp

        assert final is not None
        assert final.tool_invocations is not None, "Expected tool invocations"
        assert len(final.tool_invocations) >= 1, "Expected at least one tool call"
        inv = final.tool_invocations[0]
        assert inv["toolName"] == "get_weather", f"Expected 'get_weather', got {inv['toolName']!r}"
        assert "city" in inv["args"], f"Expected 'city' in args, got {inv['args']!r}"
        assert inv["id"], "Tool call should have a non-empty id"

    async def test_usage_stats_populated(self):
        """After a real call, input_tokens and output_tokens are > 0."""
        provider = _make_openai_provider(openai_key)
        messages = [{"role": "user", "content": "Say 'test' and nothing else."}]

        async for _ in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            pass

        stats = provider.get_stats()
        assert stats.input_tokens > 0, f"input_tokens should be > 0, got {stats.input_tokens}"
        assert stats.output_tokens > 0, f"output_tokens should be > 0, got {stats.output_tokens}"
        assert stats.requests == 1, f"requests should be 1, got {stats.requests}"

    async def test_cost_is_nonzero(self):
        """After a real call, cost is > 0 (proves OpenAI cost calculation works end-to-end)."""
        provider = _make_openai_provider(openai_key)
        messages = [{"role": "user", "content": "Say 'test' and nothing else."}]

        async for _ in provider.generate_stream(messages, tools=[], tool_choice="auto"):
            pass

        stats = provider.get_stats()
        assert stats.cost > 0, f"cost should be > 0, got {stats.cost}"

    async def test_usage_stats_after_tool_call(self):
        """After a tool-call round-trip, usage stats are populated."""
        provider = _make_openai_provider(openai_key)
        messages = [
            {"role": "user", "content": "What is the weather in Paris? Use the get_weather tool."},
        ]

        async for _ in provider.generate_stream(
            messages, tools=WEATHER_TOOL, tool_choice="auto"
        ):
            pass

        stats = provider.get_stats()
        assert stats.input_tokens > 0, f"input_tokens should be > 0, got {stats.input_tokens}"
        assert stats.output_tokens > 0, f"output_tokens should be > 0, got {stats.output_tokens}"
        assert stats.cost > 0, f"cost should be > 0 after tool call, got {stats.cost}"

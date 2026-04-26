"""Tests for OpenAIProvider — instantiation, capabilities, retry, args, stats, streaming."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.llm.config import LLMConfig
from strix.llm.provider_base import LLMRequestFailedError, LLMResponse, ProviderBase, RequestStats
from strix.llm.provider_openai import OpenAIProvider


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(**overrides):
    """Build a minimal LLMConfig-like object for testing.

    LLMConfig resolves env vars in __init__, so we mock the class to avoid
    needing STRIX_LLM set.
    """
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = overrides.get("canonical_model", "openai/gpt-5.4")
    cfg.litellm_model = overrides.get("litellm_model", "openai/gpt-5.4")
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key", None)
    cfg.api_base = overrides.get("api_base", None)
    return cfg


@pytest.fixture
def provider():
    with patch("strix.llm.provider_openai.AsyncOpenAI"):
        return OpenAIProvider(_make_config(), reasoning_effort="high")


# ---------------------------------------------------------------------------
# Instantiation & ABC compliance
# ---------------------------------------------------------------------------


class TestOpenAIProviderInstantiation:
    def test_is_subclass_of_provider_base(self, provider):
        assert isinstance(provider, ProviderBase)

    def test_initial_stats_are_zero(self, provider):
        stats = provider.get_stats()
        assert isinstance(stats, RequestStats)
        assert stats.input_tokens == 0
        assert stats.output_tokens == 0
        assert stats.requests == 0
        assert stats.cost == 0.0

    def test_get_model_name_returns_stripped(self, provider):
        # openai/ prefix is stripped from litellm_model
        assert provider.get_model_name() == "gpt-5.4"

    def test_implements_all_abstract_methods(self):
        """Verify OpenAIProvider is not abstract — all methods implemented."""
        import inspect

        abstract = {
            name
            for name, method in inspect.getmembers(ProviderBase, predicate=inspect.isfunction)
            if getattr(method, "__isabstractmethod__", False)
        }
        for method_name in abstract:
            assert hasattr(OpenAIProvider, method_name), f"Missing: {method_name}"
            assert not getattr(
                getattr(OpenAIProvider, method_name), "__isabstractmethod__", False
            ), f"Still abstract: {method_name}"


# ---------------------------------------------------------------------------
# Capability queries
# ---------------------------------------------------------------------------


class TestCapabilityQueries:
    @pytest.mark.parametrize(
        "model",
        ["gpt-5", "gpt-5.1", "gpt-5.2", "gpt-5.4", "gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    )
    def test_supports_vision_true(self, model):
        with patch("strix.llm.provider_openai.AsyncOpenAI"):
            prov = OpenAIProvider(
                _make_config(litellm_model=f"openai/{model}"), reasoning_effort="high"
            )
        assert prov.supports_vision() is True

    @pytest.mark.parametrize("model", ["gpt-5.4-turbo", "gpt-4o-2024-05-13"])
    def test_supports_vision_true_for_dash_variants(self, model):
        with patch("strix.llm.provider_openai.AsyncOpenAI"):
            prov = OpenAIProvider(
                _make_config(litellm_model=f"openai/{model}"), reasoning_effort="high"
            )
        assert prov.supports_vision() is True

    def test_supports_vision_false_for_gpt35(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI"):
            prov = OpenAIProvider(
                _make_config(litellm_model="openai/gpt-3.5-turbo"), reasoning_effort="high"
            )
        assert prov.supports_vision() is False

    def test_supports_vision_false_for_base_gpt4(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI"):
            prov = OpenAIProvider(
                _make_config(litellm_model="openai/gpt-4"), reasoning_effort="high"
            )
        assert prov.supports_vision() is False

    def test_supports_reasoning_false(self, provider):
        assert provider.supports_reasoning() is False

    def test_supports_prompt_caching_false(self, provider):
        assert provider.supports_prompt_caching() is False


# ---------------------------------------------------------------------------
# Retry logic — should_retry
# ---------------------------------------------------------------------------


class TestShouldRetry:
    def test_no_status_code_is_retryable(self, provider):
        exc = RuntimeError("connection reset")
        assert provider.should_retry(exc) is True

    def test_rate_limit_429_is_retryable(self, provider):
        exc = Exception("rate limited")
        exc.status_code = 429  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is True

    def test_server_error_500_is_retryable(self, provider):
        exc = Exception("server error")
        exc.status_code = 500  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is True

    def test_server_error_502_is_retryable(self, provider):
        exc = Exception("bad gateway")
        exc.status_code = 502  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is True

    def test_server_error_503_is_retryable(self, provider):
        exc = Exception("service unavailable")
        exc.status_code = 503  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is True

    def test_bad_request_400_is_not_retryable(self, provider):
        exc = Exception("bad request")
        exc.status_code = 400  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is False

    def test_auth_error_401_is_not_retryable(self, provider):
        exc = Exception("unauthorized")
        exc.status_code = 401  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is False

    def test_not_found_404_is_not_retryable(self, provider):
        exc = Exception("not found")
        exc.status_code = 404  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is False


# ---------------------------------------------------------------------------
# Build completion args
# ---------------------------------------------------------------------------


class TestBuildCompletionArgs:
    def test_basic_args_structure(self, provider):
        args = provider._build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "test"}}],
            tool_choice="auto",
        )
        assert args["model"] == "gpt-5.4"
        assert args["timeout"] == 300
        assert args["tool_choice"] == "auto"
        assert args["stream"] is True
        assert args["stream_options"] == {"include_usage": True}

    def test_includes_api_key_when_set(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI") as mock_cls:
            prov = OpenAIProvider(_make_config(api_key="sk-test-123"), "high")
        # Verify the AsyncOpenAI constructor was called with api_key
        mock_cls.assert_called_once_with(api_key="sk-test-123", base_url=None)

    def test_no_api_key_when_none(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI") as mock_cls:
            prov = OpenAIProvider(_make_config(api_key=None), "high")
        mock_cls.assert_called_once_with(api_key=None, base_url=None)

    def test_includes_base_url_when_set(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI") as mock_cls:
            prov = OpenAIProvider(
                _make_config(api_base="https://custom.api.com/v1"), "high"
            )
        mock_cls.assert_called_once_with(
            api_key=None, base_url="https://custom.api.com/v1"
        )

    def test_strips_images_when_no_vision(self):
        with patch("strix.llm.provider_openai.AsyncOpenAI"):
            prov = OpenAIProvider(
                _make_config(litellm_model="openai/gpt-3.5-turbo"), "high"
            )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "look"},
                    {"type": "image_url", "image_url": {"url": "data:png;base64,x"}},
                ],
            }
        ]
        args = prov._build_completion_args(messages, tools=[], tool_choice="auto")
        # Messages should have images stripped for non-vision model
        assert "[Image removed" in args["messages"][0]["content"]

    def test_model_name_has_openai_prefix_stripped(self, provider):
        args = provider._build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )
        assert args["model"] == "gpt-5.4"
        assert not args["model"].startswith("openai/")

    def test_no_tools_omits_tool_fields(self, provider):
        args = provider._build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )
        assert "tools" not in args
        assert "tool_choice" not in args


# ---------------------------------------------------------------------------
# Usage stats tracking
# ---------------------------------------------------------------------------


class TestUsageStats:
    def test_stats_tracks_requests(self, provider):
        assert provider.get_stats().requests == 0

    def test_stats_aggregate_after_update(self, provider):
        # Simulate a usage update via internal method
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 100
        mock_usage.completion_tokens = 50
        prompt_details = MagicMock()
        prompt_details.cached_tokens = 20
        mock_usage.prompt_tokens_details = prompt_details

        provider._update_usage(mock_usage)
        stats = provider.get_stats()
        assert stats.input_tokens == 100
        assert stats.output_tokens == 50
        assert stats.cached_tokens == 20
        assert stats.cost == 0.0  # Always 0.0 for OpenAI (deferred to S03/S04)

    def test_stats_to_dict_snapshot(self, provider):
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 50
        mock_usage.completion_tokens = 25
        prompt_details = MagicMock()
        prompt_details.cached_tokens = 10
        mock_usage.prompt_tokens_details = prompt_details

        provider._update_usage(mock_usage)
        snapshot = provider.get_stats().to_dict()
        assert snapshot["input_tokens"] == 50
        assert snapshot["output_tokens"] == 25
        assert snapshot["cached_tokens"] == 10
        assert snapshot["cost"] == 0.0
        assert snapshot["requests"] == 0


# ---------------------------------------------------------------------------
# Model name stripping
# ---------------------------------------------------------------------------


class TestModelNameStripping:
    def test_strips_openai_prefix(self):
        assert OpenAIProvider._strip_openai_prefix("openai/gpt-5.4") == "gpt-5.4"

    def test_no_prefix_unchanged(self):
        assert OpenAIProvider._strip_openai_prefix("gpt-5.4") == "gpt-5.4"

    def test_double_prefix_strips_once(self):
        # Only the first "openai/" is stripped
        assert OpenAIProvider._strip_openai_prefix("openai/openai/gpt-5.4") == "openai/gpt-5.4"


# ---------------------------------------------------------------------------
# Streaming behavior (with mocked AsyncOpenAI)
# ---------------------------------------------------------------------------


def _make_text_chunk(content: str) -> MagicMock:
    """Create a mock chunk with text delta."""
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta = MagicMock()
    chunk.choices[0].delta.content = content
    chunk.choices[0].delta.tool_calls = None
    chunk.usage = None
    return chunk


def _make_tool_call_chunk(
    index: int = 0,
    tc_id: str | None = None,
    name: str | None = None,
    arguments: str | None = None,
) -> MagicMock:
    """Create a mock chunk with tool_call delta."""
    tc = MagicMock()
    tc.index = index
    tc.id = tc_id
    tc.function = MagicMock()
    tc.function.name = name
    tc.function.arguments = arguments

    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta = MagicMock()
    chunk.choices[0].delta.content = None
    chunk.choices[0].delta.tool_calls = [tc]
    chunk.usage = None
    return chunk


def _make_usage_chunk(prompt_tokens: int, completion_tokens: int) -> MagicMock:
    """Create a mock final chunk with usage but empty choices."""
    chunk = MagicMock()
    chunk.choices = []
    chunk.usage = MagicMock()
    chunk.usage.prompt_tokens = prompt_tokens
    chunk.usage.completion_tokens = completion_tokens
    prompt_details = MagicMock()
    prompt_details.cached_tokens = 0
    chunk.usage.prompt_tokens_details = prompt_details
    return chunk


class _AsyncIter:
    """Helper to create a proper async iterator from a list of chunks."""

    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration


class TestStreamingBehavior:
    @pytest.mark.asyncio
    async def test_text_only_streaming(self, provider):
        """Mock chunks with only text deltas, verify accumulated content."""
        chunks = [
            _make_text_chunk("Hello"),
            _make_text_chunk(" world"),
            _make_usage_chunk(10, 5),
        ]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            responses.append(resp)

        # Should have intermediate + final response
        assert len(responses) >= 2
        # Final response should have accumulated text
        final = responses[-1]
        assert "Hello world" in final.content
        assert final.thinking_blocks is None

    @pytest.mark.asyncio
    async def test_tool_call_streaming(self, provider):
        """Mock chunks with tool_call deltas, verify tool_invocations and tool_calls."""
        chunks = [
            _make_tool_call_chunk(index=0, tc_id="call_abc", name="get_weather", arguments=None),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='{"ci'),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='ty": "SF"}'),
            _make_usage_chunk(50, 20),
        ]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "weather?"}],
            tools=[{"type": "function", "function": {"name": "get_weather"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert final.tool_invocations is not None
        assert len(final.tool_invocations) == 1
        assert final.tool_invocations[0]["toolName"] == "get_weather"
        assert final.tool_invocations[0]["args"] == {"city": "SF"}
        assert final.tool_invocations[0]["id"] == "call_abc"

        assert final.tool_calls is not None
        assert len(final.tool_calls) == 1
        assert final.tool_calls[0]["id"] == "call_abc"
        assert final.tool_calls[0]["function"]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_mixed_text_and_tool_calls(self, provider):
        """Text followed by tool calls in the same stream."""
        chunks = [
            _make_text_chunk("Let me check"),
            _make_tool_call_chunk(index=0, tc_id="call_123", name="search", arguments=None),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='{"q": "test"}'),
            _make_usage_chunk(30, 15),
        ]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "search"}],
            tools=[{"type": "function", "function": {"name": "search"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert "Let me check" in final.content
        assert final.tool_invocations is not None
        assert final.tool_invocations[0]["toolName"] == "search"

    @pytest.mark.asyncio
    async def test_usage_extraction_from_final_chunk(self, provider):
        """Verify usage stats updated from final chunk with empty choices."""
        chunks = [
            _make_text_chunk("Hi"),
            _make_usage_chunk(42, 18),
        ]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        async for _ in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            pass

        stats = provider.get_stats()
        assert stats.input_tokens == 42
        assert stats.output_tokens == 18

    @pytest.mark.asyncio
    async def test_thinking_blocks_always_none(self, provider):
        """Verify no thinking_blocks in any response from OpenAI."""
        chunks = [
            _make_text_chunk("Hello"),
            _make_usage_chunk(10, 5),
        ]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            responses.append(resp)

        for resp in responses:
            assert resp.thinking_blocks is None

    @pytest.mark.asyncio
    async def test_request_counter_increments(self, provider):
        """Verify stats.requests increments on each generate_stream call."""
        chunks = [_make_text_chunk("ok"), _make_usage_chunk(5, 2)]
        provider._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))

        assert provider.get_stats().requests == 0

        async for _ in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            pass

        assert provider.get_stats().requests == 1

    @pytest.mark.asyncio
    async def test_api_error_raises_llm_request_failed(self, provider):
        """Non-retryable errors raise LLMRequestFailedError."""
        from openai import APIStatusError

        exc = APIStatusError(
            message="Bad request",
            response=MagicMock(status_code=400, text="invalid model"),
            body=None,
        )
        provider._client.chat.completions.create = AsyncMock(side_effect=exc)

        with pytest.raises(LLMRequestFailedError, match="OpenAI request failed"):
            async for _ in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
            ):
                pass

    @pytest.mark.asyncio
    async def test_retryable_error_reraises(self, provider):
        """Retryable errors (429) reraise the original APIStatusError."""
        from openai import APIStatusError

        exc = APIStatusError(
            message="Rate limited",
            response=MagicMock(status_code=429, text="slow down"),
            body=None,
        )
        provider._client.chat.completions.create = AsyncMock(side_effect=exc)

        with pytest.raises(APIStatusError, match="Rate limited"):
            async for _ in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
            ):
                pass

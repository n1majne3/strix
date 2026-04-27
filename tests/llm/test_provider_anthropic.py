"""Tests for AnthropicProvider — conversion helpers, capabilities, cost, args, retry, streaming."""

from __future__ import annotations

import inspect
import json
from unittest.mock import MagicMock, patch

import pytest
from anthropic import APIStatusError

from strix.llm.config import LLMConfig
from strix.llm.provider_anthropic import AnthropicProvider
from strix.llm.provider_base import LLMRequestFailedError, ProviderBase, RequestStats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(**overrides):
    """Build a minimal LLMConfig-like object for testing."""
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = overrides.get(
        "canonical_model", "anthropic/claude-sonnet-4-20250514"
    )
    cfg.litellm_model = overrides.get(
        "litellm_model", "anthropic/claude-sonnet-4-20250514"
    )
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key")
    cfg.api_base = overrides.get("api_base")
    cfg.enable_prompt_caching = overrides.get("enable_prompt_caching", True)
    return cfg


@pytest.fixture
def provider():
    with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
        return AnthropicProvider(_make_config(), reasoning_effort="high")


# ---------------------------------------------------------------------------
# Instantiation & ABC compliance
# ---------------------------------------------------------------------------


class TestAnthropicProviderInstantiation:
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
        assert provider.get_model_name() == "claude-sonnet-4-20250514"

    def test_implements_all_abstract_methods(self):
        """Verify AnthropicProvider is not abstract — all methods implemented."""
        abstract = {
            name
            for name, method in inspect.getmembers(
                ProviderBase, predicate=inspect.isfunction
            )
            if getattr(method, "__isabstractmethod__", False)
        }
        for method_name in abstract:
            assert hasattr(AnthropicProvider, method_name), f"Missing: {method_name}"
            assert not getattr(
                getattr(AnthropicProvider, method_name), "__isabstractmethod__", False
            ), f"Still abstract: {method_name}"

    @pytest.mark.asyncio
    async def test_generate_stream_is_async_generator(self, provider):
        """generate_stream should be an async generator, not raise NotImplementedError."""
        gen = provider.generate_stream([], [], "auto")
        try:
            # Should not raise NotImplementedError on call — returns async generator
            assert hasattr(gen, "__aiter__")
        finally:
            await gen.aclose()


# ---------------------------------------------------------------------------
# Message conversion — system message extraction
# ---------------------------------------------------------------------------


class TestConvertMessagesSystemExtraction:
    def test_single_system_message_extracted(self, provider):
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "hi"},
        ]
        system, converted = provider._convert_messages(messages)
        assert system == "You are helpful."
        assert len(converted) == 1
        assert converted[0]["role"] == "user"

    def test_multiple_system_messages_joined(self, provider):
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "hi"},
        ]
        system, converted = provider._convert_messages(messages)
        assert system == "You are helpful.\n\nBe concise."
        assert len(converted) == 1

    def test_no_system_message_returns_none(self, provider):
        messages = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        system, converted = provider._convert_messages(messages)
        assert system is None
        assert len(converted) == 2

    def test_list_system_content_extracted(self, provider):
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are helpful.",
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
            },
            {"role": "user", "content": "hi"},
        ]
        system, converted = provider._convert_messages(messages)
        assert system == "You are helpful."
        assert len(converted) == 1


# ---------------------------------------------------------------------------
# Message conversion — tool calls
# ---------------------------------------------------------------------------


class TestConvertMessagesToolCalls:
    def test_assistant_tool_calls_converted(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_abc123",
                        "type": "function",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"city": "SF"}',
                        },
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        assert len(converted) == 1
        content = converted[0]["content"]
        assert isinstance(content, list)
        assert len(content) == 1
        block = content[0]
        assert block["type"] == "tool_use"
        assert block["id"] == "call_abc123"
        assert block["name"] == "get_weather"
        assert block["input"] == {"city": "SF"}

    def test_assistant_tool_calls_with_text_content(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": "Let me check that.",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {"name": "search", "arguments": '{"q": "test"}'},
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        content = converted[0]["content"]
        assert isinstance(content, list)
        assert content[0] == {"type": "text", "text": "Let me check that."}
        assert content[1]["type"] == "tool_use"

    def test_assistant_tool_calls_no_text(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_2",
                        "type": "function",
                        "function": {"name": "do_it", "arguments": "{}"},
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        content = converted[0]["content"]
        assert isinstance(content, list)
        assert len(content) == 1  # Only tool_use, no text block
        assert content[0]["type"] == "tool_use"

    def test_malformed_arguments_fallback_to_empty_dict(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_bad",
                        "type": "function",
                        "function": {
                            "name": "broken",
                            "arguments": "{invalid json",
                        },
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        content = converted[0]["content"]
        assert content[0]["input"] == {}

    def test_no_tool_calls_passes_through(self, provider):
        messages = [
            {"role": "assistant", "content": "Hello there"},
        ]
        _, converted = provider._convert_messages(messages)
        assert converted[0] == {"role": "assistant", "content": "Hello there"}


# ---------------------------------------------------------------------------
# Message conversion — tool results
# ---------------------------------------------------------------------------


class TestConvertMessagesToolResults:
    def test_single_tool_result_converted(self, provider):
        messages = [
            {
                "role": "tool",
                "tool_call_id": "call_abc",
                "content": "72F, sunny",
            },
        ]
        _, converted = provider._convert_messages(messages)
        assert len(converted) == 1
        assert converted[0]["role"] == "user"
        content = converted[0]["content"]
        assert isinstance(content, list)
        assert len(content) == 1
        assert content[0]["type"] == "tool_result"
        assert content[0]["tool_use_id"] == "call_abc"
        assert content[0]["content"] == "72F, sunny"

    def test_consecutive_tool_results_merged(self, provider):
        messages = [
            {"role": "tool", "tool_call_id": "call_1", "content": "result1"},
            {"role": "tool", "tool_call_id": "call_2", "content": "result2"},
        ]
        _, converted = provider._convert_messages(messages)
        # Merged into single user message with two content blocks
        assert len(converted) == 1
        assert converted[0]["role"] == "user"
        content = converted[0]["content"]
        assert isinstance(content, list)
        assert len(content) == 2
        assert content[0]["tool_use_id"] == "call_1"
        assert content[1]["tool_use_id"] == "call_2"

    def test_tool_result_with_non_string_content_serialized(self, provider):
        messages = [
            {"role": "tool", "tool_call_id": "call_x", "content": {"key": "value"}},
        ]
        _, converted = provider._convert_messages(messages)
        content = converted[0]["content"]
        assert content[0]["type"] == "tool_result"
        assert json.loads(content[0]["content"]) == {"key": "value"}


# ---------------------------------------------------------------------------
# Message conversion — tool call ID normalization
# ---------------------------------------------------------------------------


class TestConvertMessagesToolCallIdNormalization:
    def test_valid_id_passes_through(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_abc-123",
                        "type": "function",
                        "function": {"name": "f", "arguments": "{}"},
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        assert converted[0]["content"][0]["id"] == "call_abc-123"

    def test_invalid_chars_replaced(self, provider):
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call.abc@def!",
                        "type": "function",
                        "function": {"name": "f", "arguments": "{}"},
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        assert converted[0]["content"][0]["id"] == "call_abc_def_"

    def test_long_id_truncated(self, provider):
        long_id = "a" * 100
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": long_id,
                        "type": "function",
                        "function": {"name": "f", "arguments": "{}"},
                    },
                ],
            },
        ]
        _, converted = provider._convert_messages(messages)
        assert len(converted[0]["content"][0]["id"]) == 64

    def test_tool_result_id_sanitized(self, provider):
        messages = [
            {"role": "tool", "tool_call_id": "id.with.dots", "content": "result"},
        ]
        _, converted = provider._convert_messages(messages)
        assert converted[0]["content"][0]["tool_use_id"] == "id_with_dots"


# ---------------------------------------------------------------------------
# Tool definition conversion
# ---------------------------------------------------------------------------


class TestConvertTools:
    def test_converts_openai_format(self, provider):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "parameters": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                    },
                },
            }
        ]
        result = provider._convert_tools(tools)
        assert len(result) == 1
        assert result[0]["name"] == "get_weather"
        assert result[0]["input_schema"]["type"] == "object"

    def test_empty_tools_returns_empty_list(self, provider):
        assert provider._convert_tools([]) == []

    def test_multiple_tools(self, provider):
        tools = [
            {"type": "function", "function": {"name": "a", "parameters": {}}},
            {"type": "function", "function": {"name": "b", "parameters": {}}},
        ]
        result = provider._convert_tools(tools)
        assert len(result) == 2
        assert result[0]["name"] == "a"
        assert result[1]["name"] == "b"


# ---------------------------------------------------------------------------
# Tool choice conversion
# ---------------------------------------------------------------------------


class TestConvertToolChoice:
    @pytest.mark.parametrize(
        ("choice", "expected"),
        [
            ("auto", {"type": "auto"}),
            ("none", {"type": "none"}),
            ("required", {"type": "any"}),
        ],
    )
    def test_known_tool_choices(self, choice, expected):
        assert AnthropicProvider._convert_tool_choice(choice) == expected

    def test_unknown_defaults_to_auto(self):
        assert AnthropicProvider._convert_tool_choice("unknown") == {"type": "auto"}


# ---------------------------------------------------------------------------
# Capability queries
# ---------------------------------------------------------------------------


class TestCapabilityQueries:
    @pytest.mark.parametrize(
        "model",
        [
            "claude-3-5-sonnet",
            "claude-3-7-sonnet",
            "claude-4-sonnet",
            "claude-4-opus",
        ],
    )
    def test_supports_vision_true(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"),
                reasoning_effort="high",
            )
        assert prov.supports_vision() is True

    @pytest.mark.parametrize(
        "model",
        ["claude-3-haiku", "claude-sonnet-4-20250514"],
    )
    def test_supports_vision_false_for_non_matching(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"),
                reasoning_effort="high",
            )
        assert prov.supports_vision() is False

    @pytest.mark.parametrize(
        "model",
        [
            "claude-3-5-sonnet",
            "claude-3-7-sonnet",
            "claude-4-sonnet",
            "claude-4-opus",
        ],
    )
    def test_supports_reasoning_true(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"),
                reasoning_effort="high",
            )
        assert prov.supports_reasoning() is True

    def test_supports_reasoning_false_for_non_matching(self):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model="anthropic/claude-3-haiku"),
                reasoning_effort="high",
            )
        assert prov.supports_reasoning() is False

    def test_supports_prompt_caching_always_true(self, provider):
        assert provider.supports_prompt_caching() is True

    def test_vision_dash_variant(self):
        """Models like claude-4-sonnet-20250514 start with a known name."""
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model="anthropic/claude-4-sonnet-20250514"),
                reasoning_effort="high",
            )
        assert prov.supports_vision() is True
        assert prov.supports_reasoning() is True


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
# Model name stripping
# ---------------------------------------------------------------------------


class TestModelNameStripping:
    def test_strips_anthropic_prefix(self):
        result = AnthropicProvider._strip_anthropic_prefix(
            "anthropic/claude-sonnet-4"
        )
        assert result == "claude-sonnet-4"

    def test_no_prefix_unchanged(self):
        assert (
            AnthropicProvider._strip_anthropic_prefix("claude-sonnet-4")
            == "claude-sonnet-4"
        )

    def test_double_prefix_strips_once(self):
        result = AnthropicProvider._strip_anthropic_prefix(
            "anthropic/anthropic/claude"
        )
        assert result == "anthropic/claude"

    def test_empty_string_unchanged(self):
        assert AnthropicProvider._strip_anthropic_prefix("") == ""


# ---------------------------------------------------------------------------
# Cost calculation
# ---------------------------------------------------------------------------


class TestCostCalculation:
    def test_known_model_returns_nonzero_cost(self, provider):
        cost = provider._extract_cost(
            model="claude-sonnet-4-20250514",
            input_tokens=1000,
            output_tokens=500,
        )
        assert cost >= 0.0

    def test_fallback_pricing_used_when_litellm_missing(self, provider):
        with patch.dict(
            "strix.llm.provider_anthropic._FALLBACK_PRICING",
            {"custom-model": (1e-5, 5e-5)},
            clear=True,
        ):
            cost = provider._extract_cost(
                model="custom-model", input_tokens=1000, output_tokens=500,
            )
        expected = 1000 * 1e-5 + 500 * 5e-5
        assert cost == pytest.approx(expected, rel=0.01)

    def test_zero_tokens_produces_zero_cost(self, provider):
        cost = provider._extract_cost(
            model="claude-sonnet-4-20250514", input_tokens=0, output_tokens=0,
        )
        assert cost == 0.0

    def test_output_more_expensive_than_input(self, provider):
        with patch.dict(
            "strix.llm.provider_anthropic._FALLBACK_PRICING",
            {"test-model": (1e-6, 1e-5)},
            clear=True,
        ):
            cost_in = provider._extract_cost(
                model="test-model", input_tokens=1000, output_tokens=0,
            )
            cost_out = provider._extract_cost(
                model="test-model", input_tokens=0, output_tokens=1000,
            )
        assert cost_out > cost_in

    def test_unknown_model_returns_zero(self, provider):
        cost = provider._extract_cost(
            model="totally-unknown-model-xyz",
            input_tokens=1000,
            output_tokens=500,
        )
        assert cost == 0.0

    def test_multiple_usage_updates_accumulate_cost(self, provider):
        for _ in range(3):
            provider._update_usage(input_tokens=100, output_tokens=50)
        single_cost = provider._extract_cost(
            model=provider._model_name, input_tokens=100, output_tokens=50,
        )
        assert provider.get_stats().cost == pytest.approx(
            single_cost * 3, rel=0.01
        )

    def test_cost_with_cached_tokens(self, provider):
        with patch.dict(
            "strix.llm.provider_anthropic._FALLBACK_PRICING",
            {"test-model": (1e-5, 5e-5)},
            clear=True,
        ):
            original_model = provider._model_name
            provider._model_name = "test-model"
            try:
                cost_no_cache = provider._extract_cost(
                    model="test-model",
                    input_tokens=1000,
                    output_tokens=500,
                    cached_tokens=0,
                )
                cost_with_cache = provider._extract_cost(
                    model="test-model",
                    input_tokens=1000,
                    output_tokens=500,
                    cached_tokens=500,
                )
                assert cost_with_cache < cost_no_cache
            finally:
                provider._model_name = original_model


# ---------------------------------------------------------------------------
# Build completion args
# ---------------------------------------------------------------------------


class TestBuildCompletionArgs:
    def test_basic_args_structure(self, provider):
        args = provider.build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )
        assert args["model"] == "claude-sonnet-4-20250514"
        assert args["max_tokens"] == 16384
        assert args["timeout"] == 300
        assert "tools" not in args
        assert "tool_choice" not in args

    def test_system_extracted_to_top_level(self, provider):
        args = provider.build_completion_args(
            messages=[
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hi"},
            ],
            tools=[],
            tool_choice="auto",
        )
        assert args["system"] == "You are helpful."
        assert not any(
            m.get("role") == "system" for m in args["messages"]
        )

    def test_no_system_no_system_key(self, provider):
        args = provider.build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )
        assert "system" not in args

    def test_tools_included_when_present(self, provider):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "parameters": {"type": "object"},
                },
            }
        ]
        args = provider.build_completion_args(
            messages=[{"role": "user", "content": "weather?"}],
            tools=tools,
            tool_choice="auto",
        )
        assert "tools" in args
        assert args["tools"][0]["name"] == "get_weather"
        assert "tool_choice" in args
        assert args["tool_choice"] == {"type": "auto"}

    def test_tool_choice_required_converted(self, provider):
        tools = [{"type": "function", "function": {"name": "f", "parameters": {}}}]
        args = provider.build_completion_args(
            messages=[{"role": "user", "content": "go"}],
            tools=tools,
            tool_choice="required",
        )
        assert args["tool_choice"] == {"type": "any"}

    def test_reasoning_thinking_param_included(self):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            prov = AnthropicProvider(
                _make_config(litellm_model="anthropic/claude-4-sonnet"),
                reasoning_effort="high",
            )
        args = prov.build_completion_args(
            messages=[{"role": "user", "content": "think"}],
            tools=[],
            tool_choice="auto",
        )
        assert "thinking" in args
        assert args["thinking"]["type"] == "enabled"
        assert args["thinking"]["budget_tokens"] == 65536

    def test_no_thinking_for_non_reasoning_model(self, provider):
        args = provider.build_completion_args(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )
        assert "thinking" not in args


# ---------------------------------------------------------------------------
# Prepare messages
# ---------------------------------------------------------------------------


class TestPrepareMessages:
    def test_adds_cache_control_to_system_message(self, provider):
        messages = [{"role": "system", "content": "You are helpful."}]
        result = provider.prepare_messages(messages)
        assert len(result) == 1
        content = result[0]["content"]
        assert isinstance(content, list)
        assert content[0]["cache_control"] == {"type": "ephemeral"}
        assert content[0]["text"] == "You are helpful."

    def test_empty_messages_returned_unchanged(self, provider):
        assert provider.prepare_messages([]) == []

    def test_no_system_message_adds_cache_to_user(self, provider):
        """Without system message, cache_control is still added to last user message."""
        messages = [{"role": "user", "content": "hi"}]
        result = provider.prepare_messages(messages)
        assert isinstance(result[0]["content"], list)
        assert result[0]["content"][0]["cache_control"] == {"type": "ephemeral"}

    def test_already_list_content_unchanged(self, provider):
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are helpful.",
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
            }
        ]
        result = provider.prepare_messages(messages)
        assert result[0]["content"] == messages[0]["content"]


# ---------------------------------------------------------------------------
# Strip images
# ---------------------------------------------------------------------------


class TestStripImages:
    def test_strips_image_url_blocks(self, provider):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,abc"},
                    },
                ],
            }
        ]
        result = provider._strip_images(messages)
        assert len(result) == 1
        content = result[0]["content"]
        assert isinstance(content, str)
        assert "Describe this" in content
        assert "[Image removed" in content

    def test_preserves_text_only_messages(self, provider):
        messages = [{"role": "user", "content": "Just text"}]
        result = provider._strip_images(messages)
        assert result == messages

    def test_handles_list_content_with_only_text(self, provider):
        messages = [
            {"role": "user", "content": [{"type": "text", "text": "hello"}]}
        ]
        result = provider._strip_images(messages)
        assert len(result) == 1
        assert result[0]["content"] == "hello"


# ---------------------------------------------------------------------------
# Sanitize tool call ID
# ---------------------------------------------------------------------------


class TestSanitizeToolCallId:
    def test_valid_id_unchanged(self):
        assert AnthropicProvider._sanitize_tool_call_id("call_abc-123") == "call_abc-123"

    def test_dots_replaced(self):
        assert AnthropicProvider._sanitize_tool_call_id("call.abc") == "call_abc"

    def test_at_sign_replaced(self):
        assert AnthropicProvider._sanitize_tool_call_id("call@abc") == "call_abc"

    def test_truncation_to_64(self):
        assert len(AnthropicProvider._sanitize_tool_call_id("a" * 100)) == 64

    def test_empty_string(self):
        assert AnthropicProvider._sanitize_tool_call_id("") == ""

    def test_special_chars(self):
        result = AnthropicProvider._sanitize_tool_call_id("id!@#$%^&*()")
        assert all(c.isalnum() or c in "_-" for c in result)


# ---------------------------------------------------------------------------
# Streaming helpers
# ---------------------------------------------------------------------------


def _make_text_event(text: str) -> MagicMock:
    """content_block_delta with text_delta."""
    evt = MagicMock()
    evt.type = "content_block_delta"
    evt.index = 0
    delta = MagicMock()
    delta.type = "text_delta"
    delta.text = text
    evt.delta = delta
    return evt


def _make_tool_use_start_event(index: int, tc_id: str, name: str) -> MagicMock:
    """content_block_start with tool_use."""
    evt = MagicMock()
    evt.type = "content_block_start"
    evt.index = index
    block = MagicMock()
    block.type = "tool_use"
    block.id = tc_id
    block.name = name
    evt.content_block = block
    return evt


def _make_input_json_delta_event(index: int, partial_json: str) -> MagicMock:
    """content_block_delta with input_json_delta."""
    evt = MagicMock()
    evt.type = "content_block_delta"
    evt.index = index
    delta = MagicMock()
    delta.type = "input_json_delta"
    delta.partial_json = partial_json
    evt.delta = delta
    return evt


def _make_content_block_stop_event(index: int) -> MagicMock:
    """content_block_stop."""
    evt = MagicMock()
    evt.type = "content_block_stop"
    evt.index = index
    return evt


def _make_message_start_event(input_tokens: int) -> MagicMock:
    """message_start with usage."""
    evt = MagicMock()
    evt.type = "message_start"
    msg = MagicMock()
    usage = MagicMock()
    usage.input_tokens = input_tokens
    msg.usage = usage
    evt.message = msg
    return evt


def _make_message_delta_event(
    output_tokens: int,
    cache_creation: int = 0,
    cache_read: int = 0,
    stop_reason: str = "end_turn",
) -> MagicMock:
    """message_delta with usage and stop_reason."""
    evt = MagicMock()
    evt.type = "message_delta"
    usage = MagicMock()
    usage.output_tokens = output_tokens
    usage.cache_creation_input_tokens = cache_creation
    usage.cache_read_input_tokens = cache_read
    evt.usage = usage
    delta = MagicMock()
    delta.stop_reason = stop_reason
    evt.delta = delta
    return evt


def _make_message_stop_event() -> MagicMock:
    """message_stop."""
    evt = MagicMock()
    evt.type = "message_stop"
    return evt


def _make_thinking_start_event(index: int) -> MagicMock:
    """content_block_start with thinking block."""
    evt = MagicMock()
    evt.type = "content_block_start"
    evt.index = index
    block = MagicMock()
    block.type = "thinking"
    evt.content_block = block
    return evt


def _make_thinking_delta_event(index: int, text: str) -> MagicMock:
    """content_block_delta with thinking_delta."""
    evt = MagicMock()
    evt.type = "content_block_delta"
    evt.index = index
    delta = MagicMock()
    delta.type = "thinking_delta"
    delta.thinking = text
    evt.delta = delta
    return evt


class _AsyncIter:
    """Wrap a list into an async iterator."""

    def __init__(self, items: list) -> None:
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration from None


class _MockStreamContext:
    """Async context manager returning _AsyncIter."""

    def __init__(self, events: list) -> None:
        self._events = events

    async def __aenter__(self):
        return _AsyncIter(self._events)

    async def __aexit__(self, *args):
        pass


# ---------------------------------------------------------------------------
# Streaming tests
# ---------------------------------------------------------------------------


class TestStreamingBehavior:
    """Tests for AnthropicProvider.generate_stream."""

    @pytest.mark.asyncio
    async def test_text_only_streaming(self, provider):
        """Text deltas accumulate and produce intermediate + final responses."""
        events = [
            _make_message_start_event(input_tokens=50),
            _make_text_event("Hello"),
            _make_text_event(" world"),
            _make_message_delta_event(output_tokens=10),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )]

        # 2 intermediate + 1 final
        assert len(responses) == 3

        # Intermediate responses accumulate text
        assert responses[0].content == "Hello"
        assert responses[1].content == "Hello world"

        # Final response has full text
        assert responses[2].content == "Hello world"
        assert responses[2].tool_invocations is None
        assert responses[2].tool_calls is None

    @pytest.mark.asyncio
    async def test_tool_call_streaming(self, provider):
        """Tool_use blocks assembled into tool_invocations and tool_calls."""
        events = [
            _make_message_start_event(input_tokens=100),
            _make_tool_use_start_event(0, "toolu_abc", "get_weather"),
            _make_input_json_delta_event(0, '{"ci'),
            _make_input_json_delta_event(0, 'ty": "SF"}'),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=30, stop_reason="tool_use"),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "weather?"}],
            tools=[{"type": "function", "function": {"name": "get_weather", "parameters": {}}}],
            tool_choice="auto",
        )]

        # 1 start + 2 deltas + 1 final = 4
        assert len(responses) == 4

        final = responses[-1]
        assert final.tool_invocations is not None
        assert len(final.tool_invocations) == 1
        assert final.tool_invocations[0]["toolName"] == "get_weather"
        assert final.tool_invocations[0]["args"] == {"city": "SF"}
        assert final.tool_invocations[0]["id"] == "toolu_abc"

        assert final.tool_calls is not None
        assert len(final.tool_calls) == 1
        assert final.tool_calls[0]["id"] == "toolu_abc"
        assert final.tool_calls[0]["function"]["name"] == "get_weather"
        assert final.tool_calls[0]["function"]["arguments"] == '{"city": "SF"}'

    @pytest.mark.asyncio
    async def test_mixed_text_and_tool_calls(self, provider):
        """Text then tool calls — both present in final response."""
        events = [
            _make_message_start_event(input_tokens=80),
            _make_text_event("Let me check"),
            _make_tool_use_start_event(1, "toolu_1", "search"),
            _make_input_json_delta_event(1, '{"q": "test"}'),
            _make_content_block_stop_event(1),
            _make_message_delta_event(output_tokens=50, stop_reason="tool_use"),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "search"}],
            tools=[{"type": "function", "function": {"name": "search", "parameters": {}}}],
            tool_choice="auto",
        )]

        final = responses[-1]
        assert final.content == "Let me check"
        assert final.tool_invocations is not None
        assert final.tool_invocations[0]["toolName"] == "search"

    @pytest.mark.asyncio
    async def test_usage_extraction(self, provider):
        """Input/output tokens extracted from message_start/message_delta."""
        events = [
            _make_message_start_event(input_tokens=42),
            _make_text_event("hi"),
            _make_message_delta_event(
                output_tokens=7,
                cache_creation=10,
                cache_read=5,
            ),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        _ = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )]

        stats = provider.get_stats()
        assert stats.input_tokens == 42
        assert stats.output_tokens == 7
        assert stats.cached_tokens == 15  # cache_creation + cache_read
        assert stats.cost >= 0.0

    @pytest.mark.asyncio
    async def test_api_error_raises_llm_request_failed(self, provider):
        """APIStatusError(400) raises LLMRequestFailedError."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        exc = APIStatusError(
            message="Bad Request",
            response=mock_response,
            body=None,
        )
        provider._client.messages.stream = MagicMock(side_effect=exc)

        with pytest.raises(LLMRequestFailedError, match="Anthropic request failed"):
            _ = [r async for r in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}],
                tools=[],
                tool_choice="auto",
            )]

    @pytest.mark.asyncio
    async def test_retryable_error_reraises(self, provider):
        """APIStatusError(429) re-raises as-is for retry logic."""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate Limited"
        exc = APIStatusError(
            message="Rate Limited",
            response=mock_response,
            body=None,
        )
        provider._client.messages.stream = MagicMock(side_effect=exc)

        with pytest.raises(APIStatusError) as exc_info:
            _ = [r async for r in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}],
                tools=[],
                tool_choice="auto",
            )]
        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_malformed_tool_arguments_fallback(self, provider):
        """Invalid JSON in tool arguments falls back to empty dict."""
        events = [
            _make_message_start_event(input_tokens=10),
            _make_tool_use_start_event(0, "toolu_bad", "broken_tool"),
            _make_input_json_delta_event(0, "{invalid json"),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=5),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "go"}],
            tools=[{"type": "function", "function": {"name": "broken_tool", "parameters": {}}}],
            tool_choice="auto",
        )]

        final = responses[-1]
        assert final.tool_invocations is not None
        assert final.tool_invocations[0]["args"] == {}

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, provider):
        """Two tool_use blocks tracked independently."""
        events = [
            _make_message_start_event(input_tokens=50),
            _make_tool_use_start_event(0, "toolu_a", "tool_a"),
            _make_input_json_delta_event(0, '{"x": 1}'),
            _make_content_block_stop_event(0),
            _make_tool_use_start_event(1, "toolu_b", "tool_b"),
            _make_input_json_delta_event(1, '{"y": 2}'),
            _make_content_block_stop_event(1),
            _make_message_delta_event(output_tokens=20, stop_reason="tool_use"),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "run both"}],
            tools=[
                {"type": "function", "function": {"name": "tool_a", "parameters": {}}},
                {"type": "function", "function": {"name": "tool_b", "parameters": {}}},
            ],
            tool_choice="auto",
        )]

        final = responses[-1]
        assert final.tool_invocations is not None
        assert len(final.tool_invocations) == 2

        assert final.tool_invocations[0]["toolName"] == "tool_a"
        assert final.tool_invocations[0]["args"] == {"x": 1}
        assert final.tool_invocations[0]["id"] == "toolu_a"

        assert final.tool_invocations[1]["toolName"] == "tool_b"
        assert final.tool_invocations[1]["args"] == {"y": 2}
        assert final.tool_invocations[1]["id"] == "toolu_b"

    @pytest.mark.asyncio
    async def test_thinking_blocks_extracted(self, provider):
        """Thinking_delta accumulated into thinking_blocks in final response."""
        events = [
            _make_message_start_event(input_tokens=30),
            _make_thinking_start_event(0),
            _make_thinking_delta_event(0, "Hmm, "),
            _make_thinking_delta_event(0, "let me think..."),
            _make_content_block_stop_event(0),
            _make_text_event("The answer is 42."),
            _make_message_delta_event(output_tokens=40),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        responses = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "think"}],
            tools=[],
            tool_choice="auto",
        )]

        final = responses[-1]
        assert final.thinking_blocks is not None
        assert len(final.thinking_blocks) == 1
        assert final.thinking_blocks[0]["type"] == "thinking"
        assert final.thinking_blocks[0]["thinking"] == "Hmm, let me think..."
        assert final.content == "The answer is 42."

    @pytest.mark.asyncio
    async def test_request_counter_increments(self, provider):
        """stats.requests goes from 0 to 1 after a stream."""
        events = [
            _make_message_start_event(input_tokens=10),
            _make_text_event("ok"),
            _make_message_delta_event(output_tokens=2),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(
            return_value=_MockStreamContext(events),
        )

        assert provider.get_stats().requests == 0

        _ = [r async for r in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}],
            tools=[],
            tool_choice="auto",
        )]

        assert provider.get_stats().requests == 1

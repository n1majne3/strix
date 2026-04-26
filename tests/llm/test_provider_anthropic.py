"""Tests for AnthropicProvider — instantiation, capabilities, preprocessing, retry."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from strix.llm.config import LLMConfig
from strix.llm.provider_anthropic import AnthropicProvider
from strix.llm.provider_base import LLMResponse, ProviderBase, RequestStats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_config(**overrides):
    """Build a minimal LLMConfig-like object for testing.

    LLMConfig resolves env vars in __init__, so we mock the class to avoid
    needing STRIX_LLM set.
    """
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = overrides.get("canonical_model", "anthropic/claude-sonnet-4-20250514")
    cfg.litellm_model = overrides.get("litellm_model", "anthropic/claude-sonnet-4-20250514")
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key", None)
    cfg.api_base = overrides.get("api_base", None)
    cfg.enable_prompt_caching = overrides.get("enable_prompt_caching", True)
    return cfg


@pytest.fixture
def provider():
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

    def test_get_model_name_returns_canonical(self, provider):
        assert provider.get_model_name() == "anthropic/claude-sonnet-4-20250514"

    def test_implements_all_abstract_methods(self):
        """Verify AnthropicProvider is not abstract — all methods implemented."""
        import inspect

        abstract = {
            name
            for name, method in inspect.getmembers(ProviderBase, predicate=inspect.isfunction)
            if getattr(method, "__isabstractmethod__", False)
        }
        for method_name in abstract:
            assert hasattr(AnthropicProvider, method_name), f"Missing: {method_name}"
            assert not getattr(
                getattr(AnthropicProvider, method_name), "__isabstractmethod__", False
            ), f"Still abstract: {method_name}"


# ---------------------------------------------------------------------------
# Capability queries
# ---------------------------------------------------------------------------


class TestCapabilityQueries:
    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_supports_vision_true(self, mock_sv, provider):
        mock_sv.return_value = True
        assert provider.supports_vision() is True

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_supports_vision_false(self, mock_sv, provider):
        mock_sv.return_value = False
        assert provider.supports_vision() is False

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_supports_vision_exception_returns_false(self, mock_sv, provider):
        mock_sv.side_effect = ValueError("unknown model")
        assert provider.supports_vision() is False

    @patch("strix.llm.provider_anthropic.supports_reasoning")
    def test_supports_reasoning_true(self, mock_sr, provider):
        mock_sr.return_value = True
        assert provider.supports_reasoning() is True

    @patch("strix.llm.provider_anthropic.supports_reasoning")
    def test_supports_reasoning_false(self, mock_sr, provider):
        mock_sr.return_value = False
        assert provider.supports_reasoning() is False

    @patch("strix.llm.provider_anthropic.supports_prompt_caching")
    def test_supports_prompt_caching_true(self, mock_spc, provider):
        mock_spc.return_value = True
        assert provider.supports_prompt_caching() is True

    @patch("strix.llm.provider_anthropic.supports_prompt_caching")
    def test_supports_prompt_caching_false(self, mock_spc, provider):
        mock_spc.return_value = False
        assert provider.supports_prompt_caching() is False


# ---------------------------------------------------------------------------
# Message preprocessing — _strip_images
# ---------------------------------------------------------------------------


class TestStripImages:
    def test_strips_image_url_blocks(self, provider):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
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
# Message preprocessing — prepare_messages (prompt caching)
# ---------------------------------------------------------------------------


class TestPrepareMessages:
    @patch("strix.llm.provider_anthropic.supports_prompt_caching")
    def test_adds_cache_control_to_system_message(self, mock_spc, provider):
        mock_spc.return_value = True
        messages = [{"role": "system", "content": "You are helpful."}]
        result = provider.prepare_messages(messages)
        assert len(result) == 1
        content = result[0]["content"]
        assert isinstance(content, list)
        assert content[0]["cache_control"] == {"type": "ephemeral"}
        assert content[0]["text"] == "You are helpful."

    @patch("strix.llm.provider_anthropic.supports_prompt_caching")
    def test_no_cache_control_when_not_supported(self, mock_spc, provider):
        mock_spc.return_value = False
        messages = [{"role": "system", "content": "You are helpful."}]
        result = provider.prepare_messages(messages)
        assert result == messages  # unchanged

    def test_empty_messages_returned_unchanged(self, provider):
        assert provider.prepare_messages([]) == []

    @patch("strix.llm.provider_anthropic.supports_prompt_caching")
    def test_no_system_message_unchanged(self, mock_spc, provider):
        mock_spc.return_value = True
        messages = [{"role": "user", "content": "hi"}]
        result = provider.prepare_messages(messages)
        assert result == messages


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

    def test_bad_request_400_is_not_retryable(self, provider):
        exc = Exception("bad request")
        exc.status_code = 400  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is False

    def test_auth_error_401_is_not_retryable(self, provider):
        exc = Exception("unauthorized")
        exc.status_code = 401  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is False

    def test_response_status_code_attribute(self, provider):
        """should_retry also checks exc.response.status_code."""
        exc = Exception("proxy error")
        response = MagicMock()
        response.status_code = 502
        exc.response = response  # type: ignore[attr-defined]
        assert provider.should_retry(exc) is True


# ---------------------------------------------------------------------------
# build_completion_args
# ---------------------------------------------------------------------------


class TestBuildCompletionArgs:
    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_basic_args_structure(self, mock_sv, provider):
        mock_sv.return_value = True
        args = provider.build_completion_args([{"role": "user", "content": "hi"}])
        assert args["model"] == "anthropic/claude-sonnet-4-20250514"
        assert args["timeout"] == 300
        assert args["tool_choice"] == "auto"
        assert "stream_options" in args
        assert args["stream_options"] == {"include_usage": True}

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_strips_images_when_no_vision(self, mock_sv):
        mock_sv.return_value = False
        prov = AnthropicProvider(_make_config(), "high")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "look"},
                    {"type": "image_url", "image_url": {"url": "data:png;base64,x"}},
                ],
            }
        ]
        args = prov.build_completion_args(messages)
        # Messages passed to args should have images stripped
        assert "[Image removed" in args["messages"][0]["content"]

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_includes_api_key_when_set(self, mock_sv):
        mock_sv.return_value = True
        prov = AnthropicProvider(_make_config(api_key="sk-test-123"), "high")
        args = prov.build_completion_args([{"role": "user", "content": "hi"}])
        assert args["api_key"] == "sk-test-123"

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_no_api_key_when_none(self, mock_sv, provider):
        mock_sv.return_value = True
        args = provider.build_completion_args([{"role": "user", "content": "hi"}])
        assert "api_key" not in args


# ---------------------------------------------------------------------------
# Usage stats tracking
# ---------------------------------------------------------------------------


class TestUsageStats:
    def test_stats_tracks_requests(self, provider):
        assert provider.get_stats().requests == 0

    @patch("strix.llm.provider_anthropic.supports_vision")
    def test_stats_aggregate_after_update(self, mock_sv, provider):
        mock_sv.return_value = True
        # Simulate a usage update via internal method
        mock_response = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        mock_response.usage.cost = 0.01
        mock_response.usage.prompt_tokens_details = MagicMock()
        mock_response.usage.prompt_tokens_details.cached_tokens = 20
        mock_response._hidden_params = {}

        provider._update_usage_stats(mock_response)
        stats = provider.get_stats()
        assert stats.input_tokens == 100
        assert stats.output_tokens == 50
        assert stats.cached_tokens == 20
        assert stats.cost == 0.01

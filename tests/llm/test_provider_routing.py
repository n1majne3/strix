"""Tests for provider factory routing in get_provider()."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from strix.llm.config import LLMConfig
from strix.llm.llm import LLM, get_provider
from strix.llm.provider_anthropic import AnthropicProvider
from strix.llm.provider_base import ProviderBase
from strix.llm.provider_openai import OpenAIProvider


class TestProviderRouting:
    """get_provider() must route models to the correct provider based on canonical prefix."""

    def test_anthropic_model_routes_to_anthropic_provider(self) -> None:
        provider = get_provider(LLMConfig(model_name="anthropic/claude-sonnet-4-6"), "high")
        assert isinstance(provider, AnthropicProvider)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_openai_model_routes_to_openai_provider(self, mock_async_openai) -> None:
        provider = get_provider(LLMConfig(model_name="openai/gpt-5.4"), "high")
        assert isinstance(provider, OpenAIProvider)

    def test_strix_claude_routes_to_anthropic(self) -> None:
        """strix/claude-sonnet-4.6 → canonical is anthropic/claude-sonnet-4-6 → AnthropicProvider."""
        provider = get_provider(LLMConfig(model_name="strix/claude-sonnet-4.6"), "high")
        assert isinstance(provider, AnthropicProvider)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_strix_gpt_routes_to_openai(self, mock_async_openai) -> None:
        """strix/gpt-5.4 → canonical is openai/gpt-5.4 → OpenAIProvider."""
        provider = get_provider(LLMConfig(model_name="strix/gpt-5.4"), "high")
        assert isinstance(provider, OpenAIProvider)

    def test_unknown_prefix_defaults_to_anthropic(self) -> None:
        """Unrecognised prefixes should fall back to AnthropicProvider."""
        provider = get_provider(LLMConfig(model_name="gemini/gemini-3-pro"), "high")
        assert isinstance(provider, AnthropicProvider)

    def test_get_provider_returns_provider_base(self) -> None:
        """Both routes must return a ProviderBase subclass."""
        anthropic = get_provider(LLMConfig(model_name="anthropic/claude-sonnet-4-6"), "high")
        assert isinstance(anthropic, ProviderBase)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_get_provider_returns_provider_base_openai(self, mock_async_openai) -> None:
        openai = get_provider(LLMConfig(model_name="openai/gpt-5.4"), "high")
        assert isinstance(openai, ProviderBase)

    def test_both_providers_have_should_retry(self) -> None:
        """Both concrete providers must implement should_retry from the ABC."""
        from inspect import ismethod

        provider = get_provider(LLMConfig(model_name="anthropic/claude-sonnet-4-6"), "high")
        assert ismethod(provider.should_retry)
        assert provider.should_retry(Exception("test")) is not None

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_both_providers_have_should_retry_openai(self, mock_async_openai) -> None:
        from inspect import ismethod

        provider = get_provider(LLMConfig(model_name="openai/gpt-5.4"), "high")
        assert ismethod(provider.should_retry)
        assert provider.should_retry(Exception("test")) is not None


class TestLLMRoutingIntegration:
    """End-to-end routing through the LLM constructor."""

    def test_llm_anthropic_routing(self) -> None:
        llm = LLM(LLMConfig(model_name="anthropic/claude-sonnet-4-6"), agent_name=None)
        assert isinstance(llm._provider, AnthropicProvider)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_llm_openai_routing(self, mock_async_openai) -> None:
        llm = LLM(LLMConfig(model_name="openai/gpt-5.4"), agent_name=None)
        assert isinstance(llm._provider, OpenAIProvider)

    def test_llm_default_routing(self) -> None:
        """Model names without a recognised prefix default to AnthropicProvider."""
        llm = LLM(LLMConfig(model_name="claude-sonnet-4-20250514"), agent_name=None)
        assert isinstance(llm._provider, AnthropicProvider)

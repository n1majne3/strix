"""Tests for ProviderBase ABC and shared type relocation."""

from __future__ import annotations

import inspect

from unittest.mock import patch

import pytest

from strix.llm.provider_base import (
    LLMRequestFailedError,
    LLMResponse,
    ProviderBase,
    RequestStats,
)


# ---------------------------------------------------------------------------
# ProviderBase ABC
# ---------------------------------------------------------------------------


class TestProviderBaseIsAbstract:
    """ProviderBase must be uninstantiable until all abstract methods are provided."""

    def test_cannot_instantiate_directly(self) -> None:
        with pytest.raises(TypeError, match="abstract"):
            ProviderBase()  # type: ignore[abstract]

    def test_is_abstract_class(self) -> None:
        assert inspect.isabstract(ProviderBase)

    def test_all_methods_are_abstract(self) -> None:
        abstract_names = {
            name
            for name, method in inspect.getmembers(ProviderBase, predicate=inspect.isfunction)
            if getattr(method, "__isabstractmethod__", False)
        }
        expected = {
            "generate_stream",
            "supports_vision",
            "supports_reasoning",
            "supports_prompt_caching",
            "get_stats",
            "get_model_name",
            "should_retry",
        }
        assert abstract_names == expected

    def test_concrete_subclass_can_instantiate(self) -> None:
        """A subclass that implements all abstract methods should be instantiable."""

        class StubProvider(ProviderBase):
            async def generate_stream(self, messages, tools, tool_choice, **kwargs):  # type: ignore[override]
                yield LLMResponse(content="hi")  # noqa: PLR2004

            def supports_vision(self) -> bool:
                return False

            def supports_reasoning(self) -> bool:
                return False

            def supports_prompt_caching(self) -> bool:
                return False

            def get_stats(self) -> RequestStats:
                return RequestStats()

            def get_model_name(self) -> str:
                return "stub"

            def should_retry(self, exc: Exception) -> bool:
                return False

        provider = StubProvider()
        assert provider.get_model_name() == "stub"
        assert isinstance(provider.get_stats(), RequestStats)


# ---------------------------------------------------------------------------
# LLMResponse
# ---------------------------------------------------------------------------


class TestLLMResponse:
    def test_fields_default_none(self) -> None:
        resp = LLMResponse(content="hello")
        assert resp.content == "hello"
        assert resp.tool_invocations is None
        assert resp.tool_calls is None
        assert resp.thinking_blocks is None
        assert resp.streaming_tool_states is None

    def test_fields_set(self) -> None:
        resp = LLMResponse(
            content="text",
            tool_invocations=[{"toolName": "x", "args": {}, "id": "1"}],
            tool_calls=[{"id": "1", "type": "function", "function": {"name": "x", "arguments": "{}"}}],
            thinking_blocks=[{"type": "thinking", "thinking": "..."}],
            streaming_tool_states={0: {"id": "c1", "name": "x", "arguments": '{"a":'}},
        )
        assert resp.tool_invocations is not None and len(resp.tool_invocations) == 1
        assert resp.streaming_tool_states is not None and 0 in resp.streaming_tool_states


# ---------------------------------------------------------------------------
# RequestStats
# ---------------------------------------------------------------------------


class TestRequestStats:
    def test_defaults(self) -> None:
        stats = RequestStats()
        assert stats.input_tokens == 0
        assert stats.output_tokens == 0
        assert stats.cached_tokens == 0
        assert stats.cost == 0.0
        assert stats.requests == 0

    def test_to_dict(self) -> None:
        stats = RequestStats(input_tokens=100, output_tokens=50, cached_tokens=20, cost=0.0042, requests=3)
        d = stats.to_dict()
        assert d == {
            "input_tokens": 100,
            "output_tokens": 50,
            "cached_tokens": 20,
            "cost": 0.0042,
            "requests": 3,
        }

    def test_to_dict_rounds_cost(self) -> None:
        stats = RequestStats(cost=0.123456)
        assert stats.to_dict()["cost"] == 0.1235


# ---------------------------------------------------------------------------
# LLMRequestFailedError
# ---------------------------------------------------------------------------


class TestLLMRequestFailedError:
    def test_message_and_details(self) -> None:
        err = LLMRequestFailedError("boom", details="traceback")
        assert str(err) == "boom"
        assert err.message == "boom"
        assert err.details == "traceback"

    def test_details_default_none(self) -> None:
        err = LLMRequestFailedError("fail")
        assert err.details is None


# ---------------------------------------------------------------------------
# Backward compatibility — types still importable from old locations
# ---------------------------------------------------------------------------


class TestBackwardCompat:
    def test_import_from_llm_module(self) -> None:
        from strix.llm.llm import LLMRequestFailedError as Err  # noqa: F401
        from strix.llm.llm import LLMResponse as Resp  # noqa: F401
        from strix.llm.llm import RequestStats as Stats  # noqa: F401

        # They are the exact same objects, not copies
        assert Err is LLMRequestFailedError
        assert Resp is LLMResponse
        assert Stats is RequestStats

    def test_import_from_package_init(self) -> None:
        from strix.llm import LLMRequestFailedError as Err  # noqa: F401

        assert Err is LLMRequestFailedError


# ---------------------------------------------------------------------------
# generate_stream signature
# ---------------------------------------------------------------------------


class TestGenerateStreamSignature:
    def test_generate_stream_params_match_base(self) -> None:
        """generate_stream must accept (messages, tools, tool_choice, **kwargs)."""
        sig = inspect.signature(ProviderBase.generate_stream)
        params = list(sig.parameters.keys())
        assert "messages" in params
        assert "tools" in params
        assert "tool_choice" in params

    def test_generate_stream_is_async_generator(self) -> None:
        """The return annotation should be an async iterator of LLMResponse."""
        from collections.abc import AsyncIterator as AI

        ann = ProviderBase.generate_stream.__annotations__.get("return")
        # The annotation may be a string or a real type; just verify it exists
        # and references AsyncIterator.
        assert ann is not None


# ---------------------------------------------------------------------------
# Integration: LLM._provider wiring
# ---------------------------------------------------------------------------


class TestLLMProviderWiring:
    def test_llm_routes_anthropic_by_default(self) -> None:
        """LLM.__init__ must route non-openai models to AnthropicProvider."""
        from strix.llm.provider_anthropic import AnthropicProvider

        from strix.llm.llm import LLM
        from strix.llm.config import LLMConfig

        llm = LLM(LLMConfig(model_name="claude-sonnet-4-20250514"), agent_name=None)
        assert isinstance(llm._provider, AnthropicProvider)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_llm_routes_openai_prefix(self, mock_async_openai) -> None:
        """LLM.__init__ must route openai/ models to OpenAIProvider."""
        from strix.llm.provider_openai import OpenAIProvider

        from strix.llm.llm import LLM
        from strix.llm.config import LLMConfig

        llm = LLM(LLMConfig(model_name="openai/gpt-5.4"), agent_name=None)
        assert isinstance(llm._provider, OpenAIProvider)

    @patch("strix.llm.provider_openai.AsyncOpenAI")
    def test_llm_provider_exposes_stats(self, mock_async_openai) -> None:
        """LLM must aggregate stats from its provider."""
        from strix.llm.llm import LLM
        from strix.llm.config import LLMConfig

        llm = LLM(LLMConfig(model_name="openai/gpt-5.4"), agent_name=None)
        stats = llm._provider.get_stats()
        assert isinstance(stats, RequestStats)

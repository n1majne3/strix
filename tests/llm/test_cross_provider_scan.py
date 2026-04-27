"""Cross-provider equivalence and scan validation tests.

Proves Anthropic and OpenAI providers produce identical LLMResponse shapes,
conversation histories, and scan completion outcomes under identical
tool-calling scenarios.  Validates R013 (OpenAI-compatible backend).

No production code changes — validation-only.  All provider interactions
are fully mocked (MEM021/MEM037).
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import contextlib

from strix.llm.config import LLMConfig
from strix.llm.provider_anthropic import AnthropicProvider
from strix.llm.provider_base import LLMResponse
from strix.llm.provider_openai import OpenAIProvider
from strix.tools.executor import process_tool_invocations
from strix.tools.registry import clear_registry, register_tool


# ---------------------------------------------------------------------------
# Streaming mock helpers — reused from test_provider_openai.py pattern
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


# ---------------------------------------------------------------------------
# Provider factory helpers
# ---------------------------------------------------------------------------


def _make_anthropic_config(**overrides):
    """Build a mock LLMConfig for AnthropicProvider."""
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = overrides.get(
        "canonical_model", "anthropic/claude-sonnet-4-20250514"
    )
    cfg.litellm_model = overrides.get(
        "litellm_model", "anthropic/claude-sonnet-4-20250514"
    )
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key", None)
    cfg.api_base = overrides.get("api_base", None)
    cfg.enable_prompt_caching = overrides.get("enable_prompt_caching", False)
    return cfg


def _make_openai_config(**overrides):
    """Build a mock LLMConfig for OpenAIProvider."""
    cfg = MagicMock(spec=LLMConfig)
    cfg.canonical_model = overrides.get("canonical_model", "openai/gpt-5.4")
    cfg.litellm_model = overrides.get("litellm_model", "openai/gpt-5.4")
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key", None)
    cfg.api_base = overrides.get("api_base", None)
    return cfg


def _build_stream_response(chunks, tool_calls_data=None, content=""):
    """Build a mock response for Anthropic's stream_chunk_builder.

    The Anthropic provider calls stream_chunk_builder(chunks) after the
    streaming loop to extract tool_calls and usage stats.  With mock chunks,
    stream_chunk_builder fails (it expects real litellm objects), so we patch
    it with this builder.

    Args:
        chunks: The chunks that were streamed (used to derive usage).
        tool_calls_data: List of dicts with {id, name, arguments} for each
            tool call.  If None/empty, the response has no tool_calls.
        content: The text content to set on the response message.
    """
    response = MagicMock()

    # Build message
    message = MagicMock()
    message.content = content
    message.tool_calls = None
    message.thinking_blocks = None  # Explicitly None to pass _extract_thinking

    if tool_calls_data:
        tc_list = []
        for tc_data in tool_calls_data:
            tc = MagicMock()
            tc.id = tc_data["id"]
            tc.type = "function"
            tc.function = MagicMock()
            tc.function.name = tc_data["name"]
            tc.function.arguments = tc_data["arguments"]
            tc_list.append(tc)
        message.tool_calls = tc_list

    choice = MagicMock()
    choice.message = message
    response.choices = [choice]

    # Build usage from the usage chunk (last chunk has usage)
    usage_chunk = None
    for c in chunks:
        if getattr(c, "usage", None) and not getattr(c, "choices", None):
            usage_chunk = c
            break
        # Also check for chunks with both usage and choices (some patterns)
        if getattr(c, "usage", None):
            usage_chunk = c

    if usage_chunk:
        response.usage = usage_chunk.usage
    else:
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 0
        mock_usage.completion_tokens = 0
        mock_usage.cost = 0.0
        mock_usage.prompt_tokens_details = MagicMock()
        mock_usage.prompt_tokens_details.cached_tokens = 0
        response.usage = mock_usage

    response._hidden_params = {}
    return response


def _anthropic_stream_ctx(provider, chunks, tool_calls_data=None, content=""):
    """Return a context manager that mocks acompletion, stream_chunk_builder, and completion_cost.

    Usage::

        with _anthropic_stream_ctx(provider, chunks, tool_calls_data=[...], content="...") as mock_ac:
            async for resp in provider.generate_stream(...):
                ...

    The *tool_calls_data* list should contain dicts with ``id``, ``name``,
    ``arguments`` keys matching the chunks' tool-call deltas.
    """
    built = _build_stream_response(chunks, tool_calls_data, content)
    return _AnthropicStreamCtx(chunks, built)


class _AnthropicStreamCtx:
    """Context manager that patches acompletion, stream_chunk_builder, and completion_cost."""

    def __init__(self, chunks, built_response):
        self._chunks = chunks
        self._built = built_response
        self._stack = None

    def __enter__(self):
        self._stack = contextlib.ExitStack()
        self._stack.__enter__()
        mock_ac = self._stack.enter_context(
            patch("strix.llm.provider_anthropic.acompletion", new_callable=AsyncMock)
        )
        mock_ac.return_value = _AsyncIter(self._chunks)
        self._stack.enter_context(
            patch(
                "strix.llm.provider_anthropic.stream_chunk_builder",
                return_value=self._built,
            )
        )
        self._stack.enter_context(
            patch(
                "strix.llm.provider_anthropic.completion_cost",
                return_value=0.0,
            )
        )
        return mock_ac

    def __exit__(self, *exc):
        if self._stack:
            self._stack.__exit__(*exc)


def _extract_tool_calls_data_from_turn(turn_content, turn_tool, turn_args, turn_call_id):
    """Build tool_calls_data for stream_chunk_builder from turn parameters."""
    return [
        {
            "id": turn_call_id,
            "name": turn_tool,
            "arguments": json.dumps(turn_args),
        }
    ]


def _make_anthropic_provider():
    """Create an AnthropicProvider with mocked acompletion."""
    config = _make_anthropic_config()
    provider = AnthropicProvider(config, reasoning_effort="high")
    return provider


def _make_openai_provider():
    """Create an OpenAIProvider with mocked AsyncOpenAI client.

    Returns (provider,) so tests can set provider._client return values.
    """
    with patch("strix.llm.provider_openai.AsyncOpenAI"):
        config = _make_openai_config()
        provider = OpenAIProvider(config, reasoning_effort="high")
    return provider


# ---------------------------------------------------------------------------
# Scan tool registration (reused across scan simulation tests)
# ---------------------------------------------------------------------------


def _register_scan_tools():
    """Register minimal scan tools for simulation tests."""

    @register_tool(sandbox_execution=False)
    def think(thought: str) -> dict[str, Any]:
        """Record a thinking step during the scan."""
        return {"success": True, "message": f"Thought recorded: {thought[:100]}"}

    @register_tool(sandbox_execution=False)
    def terminal_exec(command: str, timeout: int = 30) -> dict[str, Any]:
        """Execute a terminal command."""
        return {
            "success": True,
            "exit_code": 0,
            "stdout": f"Simulated output of: {command}",
            "stderr": "",
        }

    @register_tool(sandbox_execution=False)
    def browser_navigate(url: str) -> dict[str, Any]:
        """Navigate to a URL in the browser."""
        return {
            "success": True,
            "url": url,
            "title": f"Page at {url}",
            "status_code": 200,
        }

    @register_tool(sandbox_execution=False)
    def report_vulnerability(
        title: str, description: str, severity: str, url: str = ""
    ) -> dict[str, Any]:
        """Report a discovered vulnerability."""
        return {
            "success": True,
            "vulnerability_id": f"VULN-{hash(title) % 10000:04d}",
            "title": title,
            "severity": severity,
        }

    @register_tool(sandbox_execution=False)
    def finish_scan(
        summary: str, scan_completed: bool = True, findings_count: int = 0
    ) -> dict[str, Any]:
        """Complete the scan and provide a summary."""
        return {
            "scan_completed": scan_completed,
            "summary": summary,
            "findings_count": findings_count,
        }


# ---------------------------------------------------------------------------
# Tool-response assertions
# ---------------------------------------------------------------------------


def _assert_response_equivalent(resp_a: LLMResponse, resp_b: LLMResponse, label: str):
    """Assert two LLMResponses have equivalent shapes for cross-provider parity."""
    # Content must match
    assert resp_a.content == resp_b.content, (
        f"[{label}] content mismatch: {resp_a.content!r} != {resp_b.content!r}"
    )

    # thinking_blocks must both be None for non-reasoning models
    assert resp_a.thinking_blocks is None, f"[{label}] Provider A thinking_blocks should be None"
    assert resp_b.thinking_blocks is None, f"[{label}] Provider B thinking_blocks should be None"

    # tool_invocations structure
    if resp_a.tool_invocations is None:
        assert resp_b.tool_invocations is None, f"[{label}] tool_invocations mismatch (None vs list)"
    else:
        assert resp_b.tool_invocations is not None, f"[{label}] tool_invocations mismatch (list vs None)"
        assert len(resp_a.tool_invocations) == len(resp_b.tool_invocations), (
            f"[{label}] tool_invocations count: {len(resp_a.tool_invocations)} vs {len(resp_b.tool_invocations)}"
        )
        for i, (inv_a, inv_b) in enumerate(
            zip(resp_a.tool_invocations, resp_b.tool_invocations)
        ):
            assert inv_a["toolName"] == inv_b["toolName"], (
                f"[{label}] inv[{i}] toolName: {inv_a['toolName']!r} != {inv_b['toolName']!r}"
            )
            assert inv_a["args"] == inv_b["args"], (
                f"[{label}] inv[{i}] args mismatch for {inv_a['toolName']}"
            )
            assert inv_a["id"] == inv_b["id"], (
                f"[{label}] inv[{i}] id: {inv_a['id']!r} != {inv_b['id']!r}"
            )

    # tool_calls structure
    if resp_a.tool_calls is None:
        assert resp_b.tool_calls is None, f"[{label}] tool_calls mismatch (None vs list)"
    else:
        assert resp_b.tool_calls is not None, f"[{label}] tool_calls mismatch (list vs None)"
        assert len(resp_a.tool_calls) == len(resp_b.tool_calls), (
            f"[{label}] tool_calls count: {len(resp_a.tool_calls)} vs {len(resp_b.tool_calls)}"
        )
        for i, (tc_a, tc_b) in enumerate(zip(resp_a.tool_calls, resp_b.tool_calls)):
            assert tc_a["id"] == tc_b["id"], (
                f"[{label}] tc[{i}] id: {tc_a['id']!r} != {tc_b['id']!r}"
            )
            assert tc_a["function"]["name"] == tc_b["function"]["name"], (
                f"[{label}] tc[{i}] name: {tc_a['function']['name']!r} != {tc_b['function']['name']!r}"
            )
            assert tc_a["function"]["arguments"] == tc_b["function"]["arguments"], (
                f"[{label}] tc[{i}] arguments mismatch for {tc_a['function']['name']}"
            )


# ===========================================================================
# Test: Provider Response Equivalence
# ===========================================================================


class TestProviderResponseEquivalence:
    """Both providers produce identical LLMResponse shapes for the same inputs."""

    @pytest.mark.asyncio
    async def test_text_only_response_equivalence(self):
        """Both providers produce the same final LLMResponse for text-only streams."""
        chunks = [
            _make_text_chunk("Hello"),
            _make_text_chunk(" world"),
            _make_usage_chunk(10, 5),
        ]
        messages = [{"role": "user", "content": "hi"}]

        # Anthropic provider
        anthropic = _make_anthropic_provider()
        with _anthropic_stream_ctx(anthropic, chunks, content="Hello world") as mock_ac:
            anthropic_responses = []
            async for resp in anthropic.generate_stream(messages, tools=[], tool_choice="auto"):
                anthropic_responses.append(resp)

        # OpenAI provider
        openai = _make_openai_provider()
        openai._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))
        openai_responses = []
        async for resp in openai.generate_stream(messages, tools=[], tool_choice="auto"):
            openai_responses.append(resp)

        # Both produce at least intermediate + final
        assert len(anthropic_responses) >= 2
        assert len(openai_responses) >= 2

        # Final responses must be equivalent
        _assert_response_equivalent(
            anthropic_responses[-1], openai_responses[-1], "text-only"
        )

    @pytest.mark.asyncio
    async def test_tool_call_response_equivalence(self):
        """Both providers produce the same LLMResponse shape for tool-call streams."""
        chunks = [
            _make_tool_call_chunk(index=0, tc_id="call_abc", name="get_weather", arguments=None),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='{"ci'),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='ty": "SF"}'),
            _make_usage_chunk(50, 20),
        ]
        messages = [{"role": "user", "content": "weather?"}]
        tools = [{"type": "function", "function": {"name": "get_weather"}}]

        # Anthropic provider
        anthropic = _make_anthropic_provider()
        tc_data = [{"id": "call_abc", "name": "get_weather", "arguments": '{"city": "SF"}'}]
        with _anthropic_stream_ctx(anthropic, chunks, tool_calls_data=tc_data) as mock_ac:
            anthropic_responses = []
            async for resp in anthropic.generate_stream(messages, tools=tools, tool_choice="auto"):
                anthropic_responses.append(resp)

        # OpenAI provider
        openai = _make_openai_provider()
        openai._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))
        openai_responses = []
        async for resp in openai.generate_stream(messages, tools=tools, tool_choice="auto"):
            openai_responses.append(resp)

        _assert_response_equivalent(
            anthropic_responses[-1], openai_responses[-1], "tool-call"
        )

    @pytest.mark.asyncio
    async def test_mixed_text_and_tool_call_equivalence(self):
        """Text followed by tool calls produces equivalent responses."""
        chunks = [
            _make_text_chunk("Let me check"),
            _make_tool_call_chunk(index=0, tc_id="call_123", name="search", arguments=None),
            _make_tool_call_chunk(index=0, tc_id=None, name=None, arguments='{"q": "test"}'),
            _make_usage_chunk(30, 15),
        ]
        messages = [{"role": "user", "content": "search"}]
        tools = [{"type": "function", "function": {"name": "search"}}]

        # Anthropic provider
        anthropic = _make_anthropic_provider()
        tc_data = [{"id": "call_123", "name": "search", "arguments": '{"q": "test"}'}]
        with _anthropic_stream_ctx(
            anthropic, chunks, tool_calls_data=tc_data, content="Let me check"
        ) as mock_ac:
            anthropic_responses = []
            async for resp in anthropic.generate_stream(messages, tools=tools, tool_choice="auto"):
                anthropic_responses.append(resp)

        # OpenAI provider
        openai = _make_openai_provider()
        openai._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))
        openai_responses = []
        async for resp in openai.generate_stream(messages, tools=tools, tool_choice="auto"):
            openai_responses.append(resp)

        final_a = anthropic_responses[-1]
        final_b = openai_responses[-1]
        _assert_response_equivalent(final_a, final_b, "mixed-text-tool")

    @pytest.mark.asyncio
    async def test_thinking_blocks_none_for_non_reasoning_models(self):
        """Both providers return thinking_blocks=None for non-reasoning models."""
        chunks = [_make_text_chunk("hi"), _make_usage_chunk(5, 2)]
        messages = [{"role": "user", "content": "hi"}]

        # Anthropic
        anthropic = _make_anthropic_provider()
        with _anthropic_stream_ctx(anthropic, chunks, content="hi") as mock_ac:
            async for resp in anthropic.generate_stream(messages, tools=[], tool_choice="auto"):
                assert resp.thinking_blocks is None, "Anthropic thinking_blocks should be None"

        # OpenAI
        openai = _make_openai_provider()
        openai._client.chat.completions.create = AsyncMock(return_value=_AsyncIter(chunks))
        async for resp in openai.generate_stream(messages, tools=[], tool_choice="auto"):
            assert resp.thinking_blocks is None, "OpenAI thinking_blocks should be None"


# ===========================================================================
# Test: Full Scan Simulation
# ===========================================================================


class TestFullScanSimulation:
    """Multi-turn agent loop simulation through both providers.

    Simulates: think → terminal_exec → browser_navigate →
               report_vulnerability → finish_scan
    """

    @pytest.fixture(autouse=True)
    def _setup_tools(self):
        clear_registry()
        _register_scan_tools()
        yield
        clear_registry()

    @pytest.mark.parametrize("provider_name", ["anthropic", "openai"])
    @pytest.mark.asyncio
    async def test_full_scan_loop_completes(self, provider_name):
        """Simulate a 5-turn scan loop through each provider and validate output."""
        # Define the multi-turn tool-call sequence
        turns = [
            {
                "tool": "think",
                "args": {"thought": "Starting scan of target"},
                "call_id": "call_think_001",
                "content": "",
            },
            {
                "tool": "terminal_exec",
                "args": {"command": "nmap -sV target.local", "timeout": 30},
                "call_id": "call_exec_002",
                "content": "I'll enumerate open ports first.",
            },
            {
                "tool": "browser_navigate",
                "args": {"url": "https://target.local"},
                "call_id": "call_nav_003",
                "content": "Now checking the web application.",
            },
            {
                "tool": "report_vulnerability",
                "args": {
                    "title": "XSS in search parameter",
                    "description": "Reflected XSS found in search",
                    "severity": "high",
                    "url": "https://target.local/search?q=",
                },
                "call_id": "call_vuln_004",
                "content": "Found a vulnerability!",
            },
            {
                "tool": "finish_scan",
                "args": {
                    "summary": "Scan completed with 1 finding",
                    "scan_completed": True,
                    "findings_count": 1,
                },
                "call_id": "call_finish_005",
                "content": "Scan is complete.",
            },
        ]

        # Build conversation history
        conversation_history = [
            {"role": "system", "content": "You are a security scanner."},
            {"role": "user", "content": "Scan target.local"},
        ]

        # Create provider
        if provider_name == "anthropic":
            provider = _make_anthropic_provider()
        else:
            provider = _make_openai_provider()

        # Run the scan loop
        for turn_idx, turn in enumerate(turns):
            # Build chunks that produce the expected tool call
            chunks = []
            if turn["content"]:
                chunks.append(_make_text_chunk(turn["content"]))
            chunks.append(
                _make_tool_call_chunk(
                    index=0,
                    tc_id=turn["call_id"],
                    name=turn["tool"],
                    arguments=None,
                )
            )
            args_json = json.dumps(turn["args"])
            chunks.append(
                _make_tool_call_chunk(
                    index=0, tc_id=None, name=None, arguments=args_json
                )
            )
            chunks.append(_make_usage_chunk(100 + turn_idx, 50 + turn_idx))

            # Mock the provider's streaming
            if provider_name == "anthropic":
                tc_data = [{
                    "id": turn["call_id"],
                    "name": turn["tool"],
                    "arguments": args_json,
                }]
                with _anthropic_stream_ctx(
                    provider, chunks, tool_calls_data=tc_data, content=turn["content"]
                ):
                    responses = []
                    async for resp in provider.generate_stream(
                        conversation_history, tools=[], tool_choice="auto"
                    ):
                        responses.append(resp)
            else:
                provider._client.chat.completions.create = AsyncMock(
                    return_value=_AsyncIter(chunks)
                )
                responses = []
                async for resp in provider.generate_stream(
                    conversation_history, tools=[], tool_choice="auto"
                ):
                    responses.append(resp)

            final = responses[-1]

            # Validate the final LLMResponse shape
            assert final.content == turn["content"], (
                f"[{provider_name} turn {turn_idx}] content mismatch"
            )
            assert final.tool_invocations is not None, (
                f"[{provider_name} turn {turn_idx}] tool_invocations missing"
            )
            assert len(final.tool_invocations) == 1, (
                f"[{provider_name} turn {turn_idx}] expected 1 tool invocation"
            )
            inv = final.tool_invocations[0]
            assert inv["toolName"] == turn["tool"], (
                f"[{provider_name} turn {turn_idx}] toolName mismatch"
            )
            assert inv["args"] == turn["args"], (
                f"[{provider_name} turn {turn_idx}] args mismatch"
            )
            assert inv["id"] == turn["call_id"], (
                f"[{provider_name} turn {turn_idx}] id mismatch"
            )
            assert final.thinking_blocks is None, (
                f"[{provider_name} turn {turn_idx}] thinking_blocks should be None"
            )

            # Append assistant message with tool_calls metadata
            assistant_msg = {
                "role": "assistant",
                "content": final.content,
            }
            if final.tool_calls:
                assistant_msg["tool_calls"] = final.tool_calls
            conversation_history.append(assistant_msg)

            # Process tool invocations (executes tools, appends tool messages)
            await process_tool_invocations(
                final.tool_invocations, conversation_history
            )

        # Validate final conversation history
        # Count roles
        user_msgs = [m for m in conversation_history if m["role"] == "user"]
        assistant_msgs = [m for m in conversation_history if m["role"] == "assistant"]
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]

        assert len(user_msgs) == 1, f"[{provider_name}] Expected 1 user message, got {len(user_msgs)}"
        assert len(assistant_msgs) == 5, f"[{provider_name}] Expected 5 assistant messages, got {len(assistant_msgs)}"
        assert len(tool_msgs) == 5, f"[{provider_name}] Expected 5 tool messages, got {len(tool_msgs)}"

        # Validate tool messages have correct tool_call_id
        for i, msg in enumerate(tool_msgs):
            assert "tool_call_id" in msg, (
                f"[{provider_name}] Tool msg {i} missing tool_call_id"
            )
            assert msg["tool_call_id"], (
                f"[{provider_name}] Tool msg {i} has empty tool_call_id"
            )

        # Validate no XML in conversation history
        _assert_no_xml(conversation_history)

        # Validate finish_scan was the last tool
        last_tool_msg = tool_msgs[-1]
        assert "scan_completed" in str(last_tool_msg.get("content", "")), (
            f"[{provider_name}] Last tool result should be from finish_scan"
        )

    @pytest.mark.asyncio
    async def test_both_producers_identical_history_structure(self):
        """Both providers produce conversation histories with identical structure."""
        turns = [
            {
                "tool": "think",
                "args": {"thought": "test"},
                "call_id": "call_001",
                "content": "",
            },
            {
                "tool": "finish_scan",
                "args": {"summary": "done", "scan_completed": True, "findings_count": 0},
                "call_id": "call_002",
                "content": "Scan complete.",
            },
        ]

        for provider_name in ("anthropic", "openai"):
            conversation_history = [
                {"role": "system", "content": "You are a scanner."},
                {"role": "user", "content": "Scan target"},
            ]

            if provider_name == "anthropic":
                provider = _make_anthropic_provider()
            else:
                provider = _make_openai_provider()

            for turn in turns:
                chunks = []
                if turn["content"]:
                    chunks.append(_make_text_chunk(turn["content"]))
                chunks.append(
                    _make_tool_call_chunk(
                        index=0, tc_id=turn["call_id"], name=turn["tool"], arguments=None
                    )
                )
                args_json = json.dumps(turn["args"])
                chunks.append(
                    _make_tool_call_chunk(
                        index=0, tc_id=None, name=None, arguments=args_json
                    )
                )
                chunks.append(_make_usage_chunk(50, 25))

                if provider_name == "anthropic":
                    tc_data = [{
                        "id": turn["call_id"],
                        "name": turn["tool"],
                        "arguments": args_json,
                    }]
                    with _anthropic_stream_ctx(
                        provider, chunks, tool_calls_data=tc_data, content=turn["content"]
                    ):
                        responses = []
                        async for resp in provider.generate_stream(
                            conversation_history, tools=[], tool_choice="auto"
                        ):
                            responses.append(resp)
                else:
                    provider._client.chat.completions.create = AsyncMock(
                        return_value=_AsyncIter(chunks)
                    )
                    responses = []
                    async for resp in provider.generate_stream(
                        conversation_history, tools=[], tool_choice="auto"
                    ):
                        responses.append(resp)

                final = responses[-1]
                assistant_msg = {"role": "assistant", "content": final.content}
                if final.tool_calls:
                    assistant_msg["tool_calls"] = final.tool_calls
                conversation_history.append(assistant_msg)
                await process_tool_invocations(
                    final.tool_invocations, conversation_history
                )

            # Store history for comparison (validated by parametrized structure below)
            if provider_name == "anthropic":
                anthropic_history = list(conversation_history)
            else:
                openai_history = list(conversation_history)

        # Now compare both histories have identical structure
        assert len(anthropic_history) == len(openai_history), (
            f"History length mismatch: anthropic={len(anthropic_history)}, openai={len(openai_history)}"
        )

        for i, (msg_a, msg_b) in enumerate(zip(anthropic_history, openai_history)):
            assert msg_a["role"] == msg_b["role"], (
                f"Message {i} role mismatch: {msg_a['role']} != {msg_b['role']}"
            )
            # Check tool_call_id patterns match for tool messages
            if msg_a["role"] == "tool":
                assert msg_a["tool_call_id"] == msg_b["tool_call_id"], (
                    f"Tool msg {i} tool_call_id mismatch: "
                    f"{msg_a['tool_call_id']} != {msg_b['tool_call_id']}"
                )
            # Check tool_calls on assistant messages match
            if msg_a["role"] == "assistant":
                tc_a = msg_a.get("tool_calls")
                tc_b = msg_b.get("tool_calls")
                if tc_a is None:
                    assert tc_b is None, f"Assistant msg {i}: tool_calls mismatch (None vs list)"
                else:
                    assert tc_b is not None, f"Assistant msg {i}: tool_calls mismatch (list vs None)"
                    assert len(tc_a) == len(tc_b), (
                        f"Assistant msg {i}: tool_calls count {len(tc_a)} vs {len(tc_b)}"
                    )
                    for j, (ca, cb) in enumerate(zip(tc_a, tc_b)):
                        assert ca["id"] == cb["id"], (
                            f"Assistant msg {i} tc[{j}] id mismatch"
                        )
                        assert ca["function"]["name"] == cb["function"]["name"], (
                            f"Assistant msg {i} tc[{j}] name mismatch"
                        )


# ===========================================================================
# Test: No Format Leakage
# ===========================================================================


class TestNoFormatLeakage:
    """Verify no provider-specific artifacts bleed into conversation history."""

    @pytest.fixture(autouse=True)
    def _setup_tools(self):
        clear_registry()
        _register_scan_tools()
        yield
        clear_registry()

    @pytest.mark.asyncio
    async def test_anthropic_no_openai_artifacts(self):
        """Anthropic conversation history has no OpenAI-specific internal fields."""
        chunks = [
            _make_text_chunk("Checking"),
            _make_tool_call_chunk(index=0, tc_id="call_a1", name="think", arguments=None),
            _make_tool_call_chunk(
                index=0, tc_id=None, name=None, arguments='{"thought": "test"}'
            ),
            _make_usage_chunk(10, 5),
        ]

        provider = _make_anthropic_provider()
        conversation_history = [
            {"role": "user", "content": "scan"},
        ]

        tc_data = [{"id": "call_a1", "name": "think", "arguments": '{"thought": "test"}'}]
        with _anthropic_stream_ctx(
            provider, chunks, tool_calls_data=tc_data, content="Checking"
        ):
            responses = []
            async for resp in provider.generate_stream(
                conversation_history, tools=[], tool_choice="auto"
            ):
                responses.append(resp)

        final = responses[-1]
        assistant_msg = {"role": "assistant", "content": final.content}
        if final.tool_calls:
            assistant_msg["tool_calls"] = final.tool_calls
        conversation_history.append(assistant_msg)
        await process_tool_invocations(final.tool_invocations, conversation_history)

        # Check no OpenAI-specific internal fields leaked
        _assert_no_provider_internals(conversation_history, "anthropic")
        # Check tool messages use standard role=tool with tool_call_id
        _assert_standard_tool_format(conversation_history, "anthropic")

    @pytest.mark.asyncio
    async def test_openai_no_anthropic_artifacts(self):
        """OpenAI conversation history has no Anthropic-specific internal fields."""
        chunks = [
            _make_text_chunk("Checking"),
            _make_tool_call_chunk(index=0, tc_id="call_b1", name="think", arguments=None),
            _make_tool_call_chunk(
                index=0, tc_id=None, name=None, arguments='{"thought": "test"}'
            ),
            _make_usage_chunk(10, 5),
        ]

        provider = _make_openai_provider()
        provider._client.chat.completions.create = AsyncMock(
            return_value=_AsyncIter(chunks)
        )
        conversation_history = [
            {"role": "user", "content": "scan"},
        ]

        responses = []
        async for resp in provider.generate_stream(
            conversation_history, tools=[], tool_choice="auto"
        ):
            responses.append(resp)

        final = responses[-1]
        assistant_msg = {"role": "assistant", "content": final.content}
        if final.tool_calls:
            assistant_msg["tool_calls"] = final.tool_calls
        conversation_history.append(assistant_msg)
        await process_tool_invocations(final.tool_invocations, conversation_history)

        _assert_no_provider_internals(conversation_history, "openai")
        _assert_standard_tool_format(conversation_history, "openai")

    @pytest.mark.asyncio
    async def test_no_xml_in_either_history(self):
        """Neither provider produces XML tool-calling artifacts."""
        for provider_name in ("anthropic", "openai"):
            chunks = [
                _make_tool_call_chunk(index=0, tc_id="call_x1", name="think", arguments=None),
                _make_tool_call_chunk(
                    index=0, tc_id=None, name=None, arguments='{"thought": "test"}'
                ),
                _make_usage_chunk(10, 5),
            ]

            conversation_history = [{"role": "user", "content": "scan"}]

            if provider_name == "anthropic":
                provider = _make_anthropic_provider()
                tc_data = [{"id": "call_x1", "name": "think", "arguments": '{"thought": "test"}'}]
                with _anthropic_stream_ctx(provider, chunks, tool_calls_data=tc_data):
                    responses = []
                    async for resp in provider.generate_stream(
                        conversation_history, tools=[], tool_choice="auto"
                    ):
                        responses.append(resp)
            else:
                provider = _make_openai_provider()
                provider._client.chat.completions.create = AsyncMock(
                    return_value=_AsyncIter(chunks)
                )
                responses = []
                async for resp in provider.generate_stream(
                    conversation_history, tools=[], tool_choice="auto"
                ):
                    responses.append(resp)

            final = responses[-1]
            assistant_msg = {"role": "assistant", "content": final.content}
            if final.tool_calls:
                assistant_msg["tool_calls"] = final.tool_calls
            conversation_history.append(assistant_msg)
            await process_tool_invocations(final.tool_invocations, conversation_history)

            _assert_no_xml(conversation_history)


# ---------------------------------------------------------------------------
# Shared assertion helpers
# ---------------------------------------------------------------------------


def _assert_no_xml(history: list[dict[str, Any]]) -> None:
    """Assert no XML tool-calling artifacts in conversation history."""
    xml_markers = [
        "<tool_result>",
        "</tool_result>",
        "<tool_name>",
        "</tool_name>",
        "<function=",
        "<invoke ",
        "<parameter>",
    ]
    for i, msg in enumerate(history):
        content = msg.get("content", "")
        if isinstance(content, str):
            for marker in xml_markers:
                assert marker not in content, (
                    f"XML artifact '{marker}' in message {i} (role={msg['role']}): "
                    f"{content[:200]}"
                )


def _assert_standard_tool_format(history: list[dict[str, Any]], provider: str) -> None:
    """Assert tool messages use standard role=tool with tool_call_id."""
    for i, msg in enumerate(history):
        if msg.get("role") == "tool":
            assert "tool_call_id" in msg, (
                f"[{provider}] Tool msg {i} missing tool_call_id"
            )
            assert msg["tool_call_id"], (
                f"[{provider}] Tool msg {i} has empty tool_call_id"
            )


def _assert_no_provider_internals(
    history: list[dict[str, Any]], provider: str
) -> None:
    """Assert no provider-internal fields have leaked into conversation history.

    This catches things like litellm-internal metadata, OpenAI response objects,
    or other provider-specific data structures that shouldn't be in the
    portable conversation format.
    """
    # Fields that should NOT appear in conversation messages
    forbidden_fields = {"_hidden_params", "response_metadata", "model_config"}
    for i, msg in enumerate(history):
        for field in forbidden_fields:
            assert field not in msg, (
                f"[{provider}] Provider-internal field '{field}' found in message {i}"
            )

"""Integration tests for native tool calling round-trip (T06).

Verifies the full message flow:
  system prompt → model → tool_call → execution → tool_result → model continues

Tests cover:
- Registry produces valid JSON-schema tool definitions
- LLM message preparation handles native tool calls and results
- Executor produces native tool role messages with tool_call_id
- Agent state stores tool_calls on assistant messages
- Memory compressor handles tool role messages
- Full round-trip message format consistency
- Error cases: invalid tool, missing params, execution errors
- Multiple tool calls in a single response
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.agents.state import AgentState
from strix.llm.llm import LLM, LLMResponse
from strix.llm.config import LLMConfig
from strix.llm.memory_compressor import _extract_message_text, _get_message_tokens
from strix.tools.executor import (
    _format_tool_result,
    execute_tool_with_validation,
    process_tool_invocations,
    validate_tool_availability,
)
from strix.tools.registry import (
    clear_registry,
    get_tool_by_name,
    get_tools_definitions,
    register_tool,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_registry():
    """Ensure registry is clean before and after each test."""
    clear_registry()
    yield
    clear_registry()


def _register_test_tools():
    """Register a set of simple test tools."""

    @register_tool(sandbox_execution=False)
    def think(thought: str) -> dict[str, Any]:
        """Record a thought."""
        return {"success": True, "message": f"Recorded: {thought[:50]}"}

    @register_tool(sandbox_execution=False)
    def echo(text: str, repeat: int = 1) -> dict[str, Any]:
        """Echo text back."""
        return {"success": True, "message": text * repeat}

    @register_tool(sandbox_execution=False)
    def add(a: int, b: int) -> dict[str, Any]:
        """Add two numbers."""
        return {"success": True, "result": a + b}

    @register_tool(sandbox_execution=False)
    def failing_tool(message: str) -> dict[str, Any]:
        """A tool that always fails."""
        raise RuntimeError(f"Intentional failure: {message}")

    @register_tool(sandbox_execution=False)
    def no_args_tool() -> dict[str, Any]:
        """A tool with no arguments."""
        return {"success": True}


# ---------------------------------------------------------------------------
# 1. Registry produces valid JSON-schema definitions
# ---------------------------------------------------------------------------


class TestRegistryJSONSchema:
    """Test that the registry produces valid OpenAI function-calling format."""

    def test_get_tools_definitions_format(self):
        _register_test_tools()
        definitions = get_tools_definitions()

        assert len(definitions) >= 4
        for defn in definitions:
            assert defn["type"] == "function"
            assert "function" in defn
            func = defn["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            params = func["parameters"]
            assert params["type"] == "object"
            assert "properties" in params

    def test_think_tool_definition(self):
        _register_test_tools()
        definitions = get_tools_definitions()
        think_defn = next(d for d in definitions if d["function"]["name"] == "think")
        func = think_defn["function"]
        assert "thought" in func["parameters"]["properties"]
        assert func["parameters"].get("required") == ["thought"]

    def test_echo_tool_with_optional_param(self):
        _register_test_tools()
        definitions = get_tools_definitions()
        echo_defn = next(d for d in definitions if d["function"]["name"] == "echo")
        func = echo_defn["function"]
        assert "text" in func["parameters"]["properties"]
        assert "repeat" in func["parameters"]["properties"]
        required = func["parameters"].get("required", [])
        assert "text" in required
        assert "repeat" not in required

    def test_empty_registry_returns_empty_list(self):
        definitions = get_tools_definitions()
        assert definitions == []


# ---------------------------------------------------------------------------
# 2. LLM message preparation handles native tool calls
# ---------------------------------------------------------------------------


class TestLLMMessagePreparation:
    """Test _prepare_messages converts internal history to LiteLLM API format."""

    @pytest.fixture
    def mock_llm_config(self):
        config = MagicMock(spec=LLMConfig)
        config.litellm_model = "anthropic/claude-sonnet-4-20250514"
        config.model_name = "claude-sonnet-4-20250514"
        config.canonical_model = "claude-sonnet-4-20250514"
        config.api_key = "test-key"
        config.api_base = None
        config.timeout = 30
        config.interactive = False
        config.enable_prompt_caching = False
        config.skills = []
        config.scan_mode = "deep"
        config.reasoning_effort = None
        config.system_prompt_context = {}
        return config

    def _make_llm(self, config):
        with patch.object(LLM, "_load_system_prompt", return_value="Test system prompt"):
            llm = LLM(config, agent_name=None)
        return llm

    def test_native_tool_role_messages_passed_through(self, mock_llm_config):
        llm = self._make_llm(mock_llm_config)

        history = [
            {"role": "user", "content": "Hello"},
            {
                "role": "assistant",
                "content": "Let me think.",
                "tool_calls": [
                    {
                        "id": "call_123",
                        "type": "function",
                        "function": {"name": "think", "arguments": '{"thought": "test"}'},
                    }
                ],
            },
            {"role": "tool", "tool_call_id": "call_123", "content": "Recorded: test"},
            {"role": "user", "content": "Continue"},
        ]

        prepared = llm._prepare_messages(history)

        # Should have: system, user, assistant+tool_calls, tool, user
        assert prepared[0]["role"] == "system"
        assert prepared[1]["role"] == "user"
        assert prepared[2]["role"] == "assistant"
        assert prepared[2]["tool_calls"] is not None
        assert len(prepared[2]["tool_calls"]) == 1
        assert prepared[2]["tool_calls"][0]["id"] == "call_123"
        assert prepared[3]["role"] == "tool"
        assert prepared[3]["tool_call_id"] == "call_123"
        assert prepared[4]["role"] == "user"

    def test_legacy_xml_tool_results_not_converted(self, mock_llm_config):
        """Legacy 'Tool Results:' user messages are NOT converted — passed through as-is."""
        llm = self._make_llm(mock_llm_config)

        tool_calls = [
            {
                "id": "call_legacy_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "hello"}'},
            }
        ]

        history = [
            {"role": "user", "content": "Think about X"},
            {
                "role": "assistant",
                "content": "Thinking...",
                "tool_calls": tool_calls,
            },
            {
                "role": "user",
                "content": (
                    "Tool Results:\n\n"
                    "<tool_result>\n"
                    "<tool_name>think</tool_name>\n"
                    "<result>{'success': True}</result>\n"
                    "</tool_result>"
                ),
            },
        ]

        prepared = llm._prepare_messages(history)

        # Legacy XML-format tool results should NOT be converted to tool role messages.
        # They pass through as regular user messages.
        tool_msgs = [m for m in prepared if m["role"] == "tool"]
        assert len(tool_msgs) == 0

        # The legacy content should appear as a user message, unchanged
        user_msgs = [m for m in prepared if m["role"] == "user"]
        assert any("Tool Results:" in str(m.get("content", "")) for m in user_msgs)

    def test_regular_messages_unchanged(self, mock_llm_config):
        llm = self._make_llm(mock_llm_config)

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        prepared = llm._prepare_messages(history)

        user_msgs = [m for m in prepared if m["role"] == "user"]
        assert any("Hello" in str(m.get("content", "")) for m in user_msgs)
        asst_msgs = [m for m in prepared if m["role"] == "assistant"]
        assert any("Hi there" in str(m.get("content", "")) for m in asst_msgs)


# ---------------------------------------------------------------------------
# 3. Executor produces native tool role messages
# ---------------------------------------------------------------------------


class TestExecutorToolMessages:
    """Test that process_tool_invocations produces native tool role messages."""

    @pytest.mark.asyncio
    async def test_single_tool_execution(self):
        _register_test_tools()

        invocations = [
            {
                "toolName": "think",
                "args": {"thought": "integration test"},
                "id": "call_test_1",
            }
        ]

        history = [
            {"role": "user", "content": "Think"},
            {
                "role": "assistant",
                "content": "Thinking...",
                "tool_calls": [
                    {
                        "id": "call_test_1",
                        "type": "function",
                        "function": {
                            "name": "think",
                            "arguments": '{"thought": "integration test"}',
                        },
                    }
                ],
            },
        ]

        result = await process_tool_invocations(invocations, history)

        # Should have appended a tool role message
        assert len(history) == 3
        tool_msg = history[-1]
        assert tool_msg["role"] == "tool"
        assert tool_msg["tool_call_id"] == "call_test_1"
        assert "integration test" in str(tool_msg["content"])
        assert result is False  # should_agent_finish

    @pytest.mark.asyncio
    async def test_tool_call_id_on_assistant_message_reconstructed(self):
        """Executor reconstructs tool_calls on assistant message if missing."""
        _register_test_tools()

        invocations = [
            {
                "toolName": "think",
                "args": {"thought": "test"},
                "id": "call_recon_1",
            }
        ]

        history = [
            {"role": "user", "content": "Think"},
            {"role": "assistant", "content": "Thinking..."},  # No tool_calls!
        ]

        await process_tool_invocations(invocations, history)

        # The assistant message should now have tool_calls
        assert history[1]["tool_calls"] is not None
        assert history[1]["tool_calls"][0]["id"] == "call_recon_1"
        assert history[1]["tool_calls"][0]["function"]["name"] == "think"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self):
        """Multiple tool invocations produce separate tool role messages."""
        _register_test_tools()

        invocations = [
            {"toolName": "think", "args": {"thought": "first"}, "id": "call_multi_1"},
            {"toolName": "echo", "args": {"text": "hello"}, "id": "call_multi_2"},
            {"toolName": "add", "args": {"a": 3, "b": 4}, "id": "call_multi_3"},
        ]

        history = [
            {"role": "user", "content": "Do multiple things"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": "call_multi_1",
                        "type": "function",
                        "function": {"name": "think", "arguments": '{"thought": "first"}'},
                    },
                    {
                        "id": "call_multi_2",
                        "type": "function",
                        "function": {"name": "echo", "arguments": '{"text": "hello"}'},
                    },
                    {
                        "id": "call_multi_3",
                        "type": "function",
                        "function": {"name": "add", "arguments": '{"a": 3, "b": 4}'},
                    },
                ],
            },
        ]

        result = await process_tool_invocations(invocations, history)

        # Should have 3 tool role messages appended
        assert len(history) == 5  # user + assistant + 3 tool messages
        tool_msgs = [m for m in history if m["role"] == "tool"]
        assert len(tool_msgs) == 3

        # Each should have its own tool_call_id
        tool_call_ids = {m["tool_call_id"] for m in tool_msgs}
        assert tool_call_ids == {"call_multi_1", "call_multi_2", "call_multi_3"}

        # Verify add result
        add_msg = next(m for m in tool_msgs if m["tool_call_id"] == "call_multi_3")
        assert "7" in str(add_msg["content"])

    @pytest.mark.asyncio
    async def test_no_args_tool(self):
        _register_test_tools()

        invocations = [
            {"toolName": "no_args_tool", "args": {}, "id": "call_noargs_1"},
        ]

        history = [
            {"role": "user", "content": "Run no args"},
            {"role": "assistant", "content": "", "tool_calls": [
                {"id": "call_noargs_1", "type": "function", "function": {"name": "no_args_tool", "arguments": "{}"}},
            ]},
        ]

        await process_tool_invocations(invocations, history)

        tool_msg = history[-1]
        assert tool_msg["role"] == "tool"
        assert tool_msg["tool_call_id"] == "call_noargs_1"


# ---------------------------------------------------------------------------
# 4. Agent state stores tool_calls properly
# ---------------------------------------------------------------------------


class TestAgentStateToolCalls:
    """Test that AgentState stores tool_calls and tool_call_id."""

    def test_add_message_with_tool_calls(self):
        state = AgentState(agent_name="Test Agent", max_iterations=10)
        tool_calls = [
            {
                "id": "call_state_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "test"}'},
            }
        ]

        state.add_message("assistant", "Thinking...", tool_calls=tool_calls)

        msg = state.messages[-1]
        assert msg["role"] == "assistant"
        assert msg["content"] == "Thinking..."
        assert msg["tool_calls"] == tool_calls

    def test_add_message_with_tool_call_id(self):
        state = AgentState(agent_name="Test Agent", max_iterations=10)

        state.add_message("tool", "Result data", tool_call_id="call_state_1")

        msg = state.messages[-1]
        assert msg["role"] == "tool"
        assert msg["content"] == "Result data"
        assert msg["tool_call_id"] == "call_state_1"

    def test_add_message_without_tool_metadata(self):
        state = AgentState(agent_name="Test Agent", max_iterations=10)

        state.add_message("user", "Hello")

        msg = state.messages[-1]
        assert msg["role"] == "user"
        assert msg["content"] == "Hello"
        assert "tool_calls" not in msg
        assert "tool_call_id" not in msg

    def test_round_trip_messages(self):
        """Simulate a full tool call round-trip in conversation history."""
        state = AgentState(agent_name="Test Agent", max_iterations=10)

        # User message
        state.add_message("user", "Think about testing")

        # Assistant with tool call
        tool_calls = [
            {
                "id": "call_rt_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "testing is important"}'},
            }
        ]
        state.add_message("assistant", "", tool_calls=tool_calls)

        # Tool result
        state.add_message(
            "tool",
            '{"success": true, "message": "Recorded: testing is important"}',
            tool_call_id="call_rt_1",
        )

        # Continue conversation
        state.add_message("assistant", "Done thinking!")

        history = state.get_conversation_history()
        assert len(history) == 4

        # Verify the structure
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
        assert history[1]["tool_calls"] is not None
        assert history[2]["role"] == "tool"
        assert history[2]["tool_call_id"] == "call_rt_1"
        assert history[3]["role"] == "assistant"
        assert history[3]["content"] == "Done thinking!"

    def test_conversation_history_is_mutable_reference(self):
        """get_conversation_history returns the actual messages list."""
        state = AgentState(agent_name="Test Agent", max_iterations=10)
        state.add_message("user", "Hello")

        history = state.get_conversation_history()
        assert len(history) == 1

        # Appending to history should modify state.messages
        history.append({"role": "assistant", "content": "Hi"})
        assert len(state.messages) == 2


# ---------------------------------------------------------------------------
# 5. Memory compressor handles tool messages
# ---------------------------------------------------------------------------


class TestMemoryCompressorToolMessages:
    """Test that memory compressor properly handles tool role messages."""

    def test_extract_text_from_tool_message(self):
        msg = {
            "role": "tool",
            "tool_call_id": "call_mc_1",
            "content": '{"success": true, "message": "Recorded"}',
        }
        text = _extract_message_text(msg)
        assert "[Tool result call_mc_1]" in text
        assert "Recorded" in text

    def test_extract_text_from_tool_message_with_list_content(self):
        msg = {
            "role": "tool",
            "tool_call_id": "call_mc_2",
            "content": [
                {"type": "text", "text": "Result text"},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
            ],
        }
        text = _extract_message_text(msg)
        assert "[Tool result call_mc_2]" in text
        assert "Result text" in text
        assert "[IMAGE]" in text

    def test_extract_text_from_assistant_with_tool_calls(self):
        msg = {
            "role": "assistant",
            "content": "Thinking about it",
            "tool_calls": [
                {
                    "id": "call_mc_3",
                    "type": "function",
                    "function": {"name": "think", "arguments": '{"thought": "deep"}'},
                }
            ],
        }
        text = _extract_message_text(msg)
        assert "Thinking about it" in text
        assert "[Tool call call_mc_3: think" in text
        assert "deep" in text

    def test_extract_text_from_assistant_empty_content_with_tool_calls(self):
        msg = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "call_mc_4",
                    "type": "function",
                    "function": {"name": "echo", "arguments": '{"text": "hi"}'},
                }
            ],
        }
        text = _extract_message_text(msg)
        assert "[Tool call call_mc_4: echo" in text

    def test_get_message_tokens_tool_message(self):
        msg = {
            "role": "tool",
            "tool_call_id": "call_tok_1",
            "content": "This is a tool result with some content",
        }
        tokens = _get_message_tokens(msg, "gpt-4")
        assert tokens > 0

    def test_get_message_tokens_assistant_with_tool_calls(self):
        msg = {
            "role": "assistant",
            "content": "Running tools",
            "tool_calls": [
                {
                    "id": "call_tok_2",
                    "type": "function",
                    "function": {"name": "think", "arguments": '{"thought": "long thought here"}'},
                }
            ],
        }
        tokens = _get_message_tokens(msg, "gpt-4")
        assert tokens > 0


# ---------------------------------------------------------------------------
# 6. Full round-trip message format consistency
# ---------------------------------------------------------------------------


class TestFullRoundTrip:
    """Test the complete message flow from agent through executor."""

    @pytest.mark.asyncio
    async def test_end_to_end_single_tool_round_trip(self):
        """Verify a complete single tool call round-trip message flow."""
        _register_test_tools()

        # 1. Simulate agent state
        state = AgentState(agent_name="Test Agent", max_iterations=10)

        # 2. User message
        state.add_message("user", "Think about testing")

        # 3. LLM response with tool call (as if from _process_iteration)
        tool_calls = [
            {
                "id": "call_e2e_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "testing matters"}'},
            }
        ]
        state.add_message("assistant", "", tool_calls=tool_calls)

        # 4. Tool invocations extracted from LLM response
        invocations = [
            {
                "toolName": "think",
                "args": {"thought": "testing matters"},
                "id": "call_e2e_1",
            }
        ]

        # 5. Execute tools (as base_agent._execute_actions does)
        conversation_history = state.get_conversation_history()
        result = await process_tool_invocations(invocations, conversation_history, state)

        # 6. Verify state
        assert result is False  # Agent should not finish

        # 7. Verify message structure
        history = state.get_conversation_history()
        assert len(history) == 3  # user, assistant, tool

        # User message
        assert history[0]["role"] == "user"
        assert "testing" in history[0]["content"]

        # Assistant message with tool_calls
        assert history[1]["role"] == "assistant"
        assert history[1]["tool_calls"] is not None
        assert len(history[1]["tool_calls"]) == 1
        tc = history[1]["tool_calls"][0]
        assert tc["id"] == "call_e2e_1"
        assert tc["function"]["name"] == "think"

        # Tool result message
        assert history[2]["role"] == "tool"
        assert history[2]["tool_call_id"] == "call_e2e_1"
        assert "testing matters" in str(history[2]["content"])

    @pytest.mark.asyncio
    async def test_end_to_end_multi_tool_round_trip(self):
        """Verify a multi-tool round-trip."""
        _register_test_tools()

        state = AgentState(agent_name="Test Agent", max_iterations=10)
        state.add_message("user", "Think and echo")

        tool_calls = [
            {
                "id": "call_mt_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "multi-test"}'},
            },
            {
                "id": "call_mt_2",
                "type": "function",
                "function": {"name": "echo", "arguments": '{"text": "hello world"}'},
            },
        ]
        state.add_message("assistant", "", tool_calls=tool_calls)

        invocations = [
            {"toolName": "think", "args": {"thought": "multi-test"}, "id": "call_mt_1"},
            {"toolName": "echo", "args": {"text": "hello world"}, "id": "call_mt_2"},
        ]

        conversation_history = state.get_conversation_history()
        await process_tool_invocations(invocations, conversation_history, state)

        history = state.get_conversation_history()
        tool_msgs = [m for m in history if m["role"] == "tool"]
        assert len(tool_msgs) == 2

        think_result = next(m for m in tool_msgs if m["tool_call_id"] == "call_mt_1")
        assert "multi-test" in str(think_result["content"])

        echo_result = next(m for m in tool_msgs if m["tool_call_id"] == "call_mt_2")
        assert "hello world" in str(echo_result["content"])


# ---------------------------------------------------------------------------
# 7. Error cases
# ---------------------------------------------------------------------------


class TestErrorCases:
    """Test error handling for invalid tool calls."""

    @pytest.mark.asyncio
    async def test_invalid_tool_name(self):
        """Invalid tool name returns an error string, not an exception."""
        _register_test_tools()

        result = await execute_tool_with_validation("nonexistent_tool")
        assert isinstance(result, str)
        assert "Error" in result
        assert "not available" in result

    @pytest.mark.asyncio
    async def test_missing_required_parameter(self):
        """Missing required parameter returns an error string."""
        _register_test_tools()

        result = await execute_tool_with_validation("think")  # Missing 'thought'
        assert isinstance(result, str)
        assert "Error" in result
        assert "missing required" in result.lower()

    @pytest.mark.asyncio
    async def test_tool_execution_error(self):
        """Tool that raises an exception returns an error string."""
        _register_test_tools()

        result = await execute_tool_with_validation("failing_tool", message="boom")
        assert isinstance(result, str)
        assert "Error executing failing_tool" in result
        assert "Intentional failure" in result

    @pytest.mark.asyncio
    async def test_error_result_in_tool_role_message(self):
        """Error results are still formatted as tool role messages."""
        _register_test_tools()

        invocations = [
            {"toolName": "failing_tool", "args": {"message": "test error"}, "id": "call_err_1"},
        ]

        history = [
            {"role": "user", "content": "Run failing tool"},
            {"role": "assistant", "content": "", "tool_calls": [
                {"id": "call_err_1", "type": "function", "function": {"name": "failing_tool", "arguments": '{"message": "test error"}'}},
            ]},
        ]

        # execute_tool_with_validation catches the error and returns a string,
        # so process_tool_invocations should succeed
        result = await process_tool_invocations(invocations, history)
        assert result is False

        tool_msg = history[-1]
        assert tool_msg["role"] == "tool"
        assert tool_msg["tool_call_id"] == "call_err_1"

    def test_validate_tool_availability_none_name(self):
        _register_test_tools()
        is_valid, error = validate_tool_availability(None)
        assert is_valid is False
        assert "missing" in error.lower()

    def test_validate_tool_availability_unknown(self):
        _register_test_tools()
        is_valid, error = validate_tool_availability("unknown_tool")
        assert is_valid is False
        assert "not available" in error


# ---------------------------------------------------------------------------
# 8. LLM response parsing (tool_calls extraction from LiteLLM)
# ---------------------------------------------------------------------------


class TestLLMResponseParsing:
    """Test that LLMResponse correctly carries tool_calls and tool_invocations."""

    def test_llm_response_dataclass(self):
        tool_calls = [
            {
                "id": "call_parse_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "test"}'},
            }
        ]
        tool_invocations = [
            {"toolName": "think", "args": {"thought": "test"}, "id": "call_parse_1"},
        ]

        response = LLMResponse(
            content="Thinking...",
            tool_invocations=tool_invocations,
            tool_calls=tool_calls,
        )

        assert response.content == "Thinking..."
        assert response.tool_invocations is not None
        assert response.tool_calls is not None
        assert response.tool_invocations[0]["toolName"] == "think"
        assert response.tool_calls[0]["id"] == "call_parse_1"

    def test_llm_response_text_only(self):
        response = LLMResponse(content="Just text, no tools")

        assert response.content == "Just text, no tools"
        assert response.tool_invocations is None
        assert response.tool_calls is None

    def test_llm_response_tool_only_no_text(self):
        """Tool-call-only response with empty content is valid."""
        tool_calls = [
            {
                "id": "call_to_1",
                "type": "function",
                "function": {"name": "think", "arguments": '{"thought": "test"}'},
            }
        ]

        response = LLMResponse(
            content="",
            tool_invocations=[{"toolName": "think", "args": {"thought": "test"}, "id": "call_to_1"}],
            tool_calls=tool_calls,
        )

        assert response.content == ""
        assert response.tool_calls is not None


# ---------------------------------------------------------------------------
# 9. LLM _build_completion_args includes tools
# ---------------------------------------------------------------------------


class TestBuildCompletionArgs:
    """Test that _build_completion_args includes tools parameter."""

    @pytest.fixture
    def mock_llm_config(self):
        config = MagicMock(spec=LLMConfig)
        config.litellm_model = "anthropic/claude-sonnet-4-20250514"
        config.model_name = "claude-sonnet-4-20250514"
        config.canonical_model = "claude-sonnet-4-20250514"
        config.api_key = "test-key"
        config.api_base = None
        config.timeout = 30
        config.interactive = False
        config.enable_prompt_caching = False
        config.skills = []
        config.scan_mode = "deep"
        config.reasoning_effort = None
        config.system_prompt_context = {}
        return config

    def test_tools_included_in_completion_args(self, mock_llm_config):
        _register_test_tools()

        with patch.object(LLM, "_load_system_prompt", return_value="Test"):
            llm = LLM(mock_llm_config, agent_name=None)

        with patch.object(llm._provider, "supports_vision", return_value=True):
            args = llm._provider.build_completion_args([{"role": "user", "content": "Hi"}])

        assert "tools" in args
        assert "tool_choice" in args
        assert args["tool_choice"] == "auto"
        assert isinstance(args["tools"], list)
        assert len(args["tools"]) >= 1
        # Each tool def should be in OpenAI format
        for tool_def in args["tools"]:
            assert tool_def["type"] == "function"
            assert "function" in tool_def


# ---------------------------------------------------------------------------
# 10. get_tools_definitions() format validation (T03 step 6)
# ---------------------------------------------------------------------------


class TestToolsDefinitionsFormatValidation:
    """Deep format validation for get_tools_definitions() output.

    Verifies JSON Schema compliance, type consistency, description defaults,
    and absence of any XML remnants in definitions.
    """

    def test_json_schema_property_types_match_python_types(self):
        """Property types in definitions should reflect Python type annotations."""

        @register_tool(sandbox_execution=False)
        def typed_tool(
            name: str,
            count: int,
            ratio: float,
            enabled: bool,
        ) -> dict[str, Any]:
            """A tool with various typed params."""
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "typed_tool")
        props = func_def["function"]["parameters"]["properties"]

        assert props["name"]["type"] == "string"
        assert props["count"]["type"] == "integer"
        assert props["ratio"]["type"] == "number"
        assert props["enabled"]["type"] == "boolean"

    def test_optional_params_not_in_required(self):
        """Parameters with defaults should not appear in the required list."""

        @register_tool(sandbox_execution=False)
        def optional_params(
            required_arg: str,
            optional_arg: str = "default",
            another_optional: int = 5,
        ) -> dict[str, Any]:
            """Tool with optional params."""
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "optional_params")
        required = func_def["function"]["parameters"].get("required", [])

        assert "required_arg" in required
        assert "optional_arg" not in required
        assert "another_optional" not in required

    def test_description_extracted_from_docstring(self):
        """Tool description should come from the first paragraph of the docstring."""

        @register_tool(sandbox_execution=False)
        def documented_tool(x: int) -> dict[str, Any]:
            """This is the tool description.

            This is additional detail that should not appear in the short description.
            """
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "documented_tool")
        desc = func_def["function"]["description"]

        assert desc == "This is the tool description."
        assert "additional detail" not in desc

    def test_no_xml_in_definitions(self):
        """No XML-related keys or values should appear in tool definitions."""

        @register_tool(sandbox_execution=False)
        def xml_clean_tool(x: str) -> dict[str, Any]:
            """A clean tool."""
            return {}

        defs = get_tools_definitions()
        defs_str = json.dumps(defs)

        assert "xml_schema" not in defs_str
        assert "<function" not in defs_str
        assert "</function>" not in defs_str
        assert "<invoke" not in defs_str

    def test_function_name_matches_registered_name(self):
        """The 'name' in the function definition should match the Python function name."""

        @register_tool(sandbox_execution=False)
        def my_specific_tool(x: str) -> dict[str, Any]:
            """A specific tool."""
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "my_specific_tool")
        assert func_def["function"]["name"] == "my_specific_tool"

    def test_parameters_object_has_json_schema_required_keys(self):
        """Each 'parameters' block must have 'type' and 'properties'."""

        @register_tool(sandbox_execution=False)
        def param_tool(x: str, y: int) -> dict[str, Any]:
            """Tool with params."""
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "param_tool")
        params = func_def["function"]["parameters"]

        assert params["type"] == "object"
        assert isinstance(params["properties"], dict)
        assert isinstance(params.get("required", []), list)

    def test_no_args_tool_has_empty_properties(self):
        """A tool with no args should produce empty properties dict."""

        @register_tool(sandbox_execution=False)
        def no_args_here() -> dict[str, Any]:
            """No arguments at all."""
            return {}

        defs = get_tools_definitions()
        func_def = next(d for d in defs if d["function"]["name"] == "no_args_here")
        params = func_def["function"]["parameters"]

        assert params["properties"] == {}
        assert "required" not in params or params["required"] == []


# ---------------------------------------------------------------------------
# 11. Tool result message format validation (T03 step 7)
# ---------------------------------------------------------------------------


class TestToolResultMessageFormat:
    """Validate the exact format of tool result messages produced by _format_tool_result."""

    def test_basic_string_result_format(self):
        """String result produces a tool role message with string content."""
        msg, images = _format_tool_result("test_tool", "hello world", "call_fmt_1")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_fmt_1"
        assert msg["content"] == "hello world"
        assert images == []

    def test_dict_result_converted_to_string(self):
        """Dict result is stringified in the content field."""
        result = {"success": True, "data": [1, 2, 3]}
        msg, images = _format_tool_result("test_tool", result, "call_dict_1")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_dict_1"
        assert isinstance(msg["content"], str)
        assert "success" in msg["content"]

    def test_none_result_gets_default_message(self):
        """None result produces a descriptive message instead of 'None'."""
        msg, images = _format_tool_result("my_tool", None, "call_none_1")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_none_1"
        assert "my_tool" in msg["content"]
        assert msg["content"] != "None"
        assert "executed successfully" in msg["content"]

    def test_large_result_is_truncated(self):
        """Results exceeding 10000 chars are truncated with a marker."""
        large_result = "x" * 15000
        msg, _images = _format_tool_result("big_tool", large_result, "call_big_1")

        assert msg["role"] == "tool"
        assert len(msg["content"]) < 15000
        assert "truncated" in msg["content"].lower()
        # Should preserve start and end
        assert msg["content"].startswith("xxx")
        assert msg["content"].endswith("xxx")

    def test_tool_call_id_preserved_exactly(self):
        """The tool_call_id in the message must match exactly what was passed."""
        tc_id = "call_abc123_def456"
        msg, _ = _format_tool_result("tool", "result", tc_id)

        assert msg["tool_call_id"] == tc_id

    def test_screenshot_extraction_creates_multipart_content(self):
        """Results with screenshot data produce multipart content blocks."""
        result = {"text": "page loaded", "screenshot": "base64imagedata"}
        msg, images = _format_tool_result("browser_tool", result, "call_ss_1")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_ss_1"
        # Content should be multipart (list of content blocks)
        assert isinstance(msg["content"], list)
        text_blocks = [b for b in msg["content"] if b["type"] == "text"]
        image_blocks = [b for b in msg["content"] if b["type"] == "image_url"]
        assert len(text_blocks) >= 1
        assert len(image_blocks) == 1
        # Images returned separately
        assert len(images) == 1
        assert "base64imagedata" in images[0]["image_url"]["url"]

    def test_error_string_still_produces_tool_message(self):
        """Error strings from tools should still be valid tool role messages."""
        error_result = "Error: tool execution failed"
        msg, _ = _format_tool_result("failing_tool", error_result, "call_err_fmt")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_err_fmt"
        assert "Error" in msg["content"]

    @pytest.mark.asyncio
    async def test_executor_appends_tool_messages_in_order(self):
        """process_tool_invocations appends tool messages preserving invocation order."""
        _register_test_tools()

        invocations = [
            {"toolName": "echo", "args": {"text": "first"}, "id": "call_order_1"},
            {"toolName": "echo", "args": {"text": "second"}, "id": "call_order_2"},
            {"toolName": "echo", "args": {"text": "third"}, "id": "call_order_3"},
        ]

        history = [
            {"role": "user", "content": "Test"},
            {"role": "assistant", "content": "", "tool_calls": [
                {"id": "call_order_1", "type": "function", "function": {"name": "echo", "arguments": '{"text": "first"}'}},
                {"id": "call_order_2", "type": "function", "function": {"name": "echo", "arguments": '{"text": "second"}'}},
                {"id": "call_order_3", "type": "function", "function": {"name": "echo", "arguments": '{"text": "third"}'}},
            ]},
        ]

        await process_tool_invocations(invocations, history)

        tool_msgs = [m for m in history if m["role"] == "tool"]
        assert len(tool_msgs) == 3
        # Order preserved
        assert "first" in str(tool_msgs[0]["content"])
        assert "second" in str(tool_msgs[1]["content"])
        assert "third" in str(tool_msgs[2]["content"])
        # tool_call_id matches
        assert tool_msgs[0]["tool_call_id"] == "call_order_1"
        assert tool_msgs[1]["tool_call_id"] == "call_order_2"
        assert tool_msgs[2]["tool_call_id"] == "call_order_3"

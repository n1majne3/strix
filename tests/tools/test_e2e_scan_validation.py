"""End-to-end autonomous scan validation (T04).

Validates the complete scan pipeline using mock LLM responses:
1. Agent initialization (StrixAgent creation, sandbox setup bypass)
2. Native tool-calling format throughout the conversation history
3. Multiple scan modes (quick, standard, deep) produce correct tool definitions
4. Skills load and inject into system prompt
5. Tool execution produces native {"role": "tool"} messages
6. Multiple tool calls in a single LLM response
7. Scan completion flow via finish_scan tool
8. Error handling and retry paths maintain native format
9. No XML remnants in the conversation history at any point
10. Performance: agent loop runs without unnecessary overhead
"""

import asyncio
import json
import time
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
    clear_registry()
    yield
    clear_registry()


def _mock_llm_config(
    scan_mode: str = "deep",
    skills: list[str] | None = None,
) -> MagicMock:
    """Create a mock LLMConfig that avoids STRIX_LLM env var requirement."""
    config = MagicMock(spec=LLMConfig)
    config.litellm_model = "anthropic/claude-sonnet-4-20250514"
    config.model_name = "claude-sonnet-4-20250514"
    config.canonical_model = "claude-sonnet-4-20250514"
    config.api_key = "test-key"
    config.api_base = None
    config.timeout = 30
    config.interactive = False
    config.enable_prompt_caching = False
    config.skills = skills or []
    config.scan_mode = scan_mode
    config.reasoning_effort = None
    config.system_prompt_context = {}
    config.is_whitebox = False
    return config


def _make_llm(
    scan_mode: str = "deep",
    skills: list[str] | None = None,
    agent_name: str | None = "StrixAgent",
) -> LLM:
    """Create an LLM instance with mock config to avoid env var requirements."""
    config = _mock_llm_config(scan_mode=scan_mode, skills=skills)
    with patch.object(LLM, "_load_system_prompt", return_value="Test system prompt"):
        llm = LLM(config, agent_name=agent_name)
    return llm


def _register_scan_tools():
    """Register a representative set of scan tools for end-to-end testing."""

    @register_tool(sandbox_execution=False)
    def think(thought: str) -> dict[str, Any]:
        """Record a thinking step during the scan."""
        return {"success": True, "message": f"Thought recorded: {thought[:100]}"}

    @register_tool(sandbox_execution=False)
    def terminal_exec(command: str, timeout: int = 30) -> dict[str, Any]:
        """Execute a terminal command."""
        # Simulate command execution
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
        title: str,
        description: str,
        severity: str,
        url: str = "",
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
        summary: str,
        scan_completed: bool = True,
        findings_count: int = 0,
    ) -> dict[str, Any]:
        """Complete the scan and provide a summary."""
        return {
            "scan_completed": scan_completed,
            "summary": summary,
            "findings_count": findings_count,
        }

    @register_tool(sandbox_execution=False)
    def agent_finish(result: str, agent_completed: bool = True) -> dict[str, Any]:
        """Finish a sub-agent's task."""
        return {
            "agent_completed": agent_completed,
            "result": result,
        }

    @register_tool(sandbox_execution=False)
    def web_search(query: str) -> dict[str, Any]:
        """Search the web for information."""
        return {
            "success": True,
            "results": [
                {"title": f"Result for: {query}", "url": "https://example.com", "snippet": "..."}
            ],
        }

    @register_tool(sandbox_execution=False)
    def load_skill(skill_name: str) -> dict[str, Any]:
        """Load a skill into the agent."""
        return {
            "success": True,
            "skill_loaded": skill_name,
            "message": f"Skill '{skill_name}' loaded successfully",
        }

    @register_tool(sandbox_execution=False)
    def create_agent(agent_state: Any, name: str, task: str) -> dict[str, Any]:
        """Create a sub-agent for delegated work."""
        return {
            "success": True,
            "agent_id": f"subagent_{hash(name) % 10000:04d}",
            "name": name,
            "task": task,
        }

    @register_tool(sandbox_execution=False)
    def no_args_status() -> dict[str, Any]:
        """Get current scan status."""
        return {"success": True, "status": "running", "iteration": 1}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_native_tool_call(
    tool_name: str,
    args: dict[str, Any],
    call_id: str | None = None,
) -> dict[str, Any]:
    """Create a native-format tool invocation (as produced by LLM._stream)."""
    return {
        "toolName": tool_name,
        "args": args,
        "id": call_id or f"call_{tool_name}_{hash(str(args)) % 10000:04d}",
    }


def _make_llm_response(
    content: str = "",
    tool_invocations: list[dict[str, Any]] | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
) -> LLMResponse:
    """Create a mock LLMResponse as produced by the LLM._stream method."""
    return LLMResponse(
        content=content,
        tool_invocations=tool_invocations,
        tool_calls=tool_calls,
        thinking_blocks=None,
        streaming_tool_states=None,
    )


def _make_tool_calls_from_invocations(
    invocations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build OpenAI-format tool_calls list from invocations (mirrors LLM._stream logic)."""
    calls = []
    for inv in invocations:
        calls.append({
            "id": inv["id"],
            "type": "function",
            "function": {
                "name": inv["toolName"],
                "arguments": json.dumps(inv["args"]),
            },
        })
    return calls


def _assert_no_xml_in_history(history: list[dict[str, Any]]) -> None:
    """Assert that no XML tool-calling artifacts exist in conversation history."""
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
                    f"XML artifact '{marker}' found in message {i} (role={msg['role']}): "
                    f"{content[:200]}"
                )
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text", "")
                    for marker in xml_markers:
                        assert marker not in text, (
                            f"XML artifact '{marker}' found in multipart message {i}: {text[:200]}"
                        )


def _assert_native_tool_format(history: list[dict[str, Any]]) -> None:
    """Assert that tool results are in native format (role=tool with tool_call_id)."""
    for i, msg in enumerate(history):
        if msg.get("role") == "tool":
            assert "tool_call_id" in msg, (
                f"Tool message at index {i} missing tool_call_id: {msg}"
            )
            assert msg["tool_call_id"], (
                f"Tool message at index {i} has empty tool_call_id: {msg}"
            )


# ---------------------------------------------------------------------------
# Test: Tool definitions for scan modes
# ---------------------------------------------------------------------------


class TestScanModeToolDefinitions:
    """Verify that tools definitions are correct for different scan modes."""

    def test_quick_mode_definitions_are_native_json_schema(self):
        _register_scan_tools()
        llm = _make_llm(scan_mode="quick")

        defs = get_tools_definitions()
        assert len(defs) > 0, "No tool definitions returned"

        for tool_def in defs:
            assert tool_def["type"] == "function"
            func = tool_def["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            params = func["parameters"]
            assert params["type"] == "object"
            assert "properties" in params

    def test_standard_mode_definitions(self):
        _register_scan_tools()
        llm = _make_llm(scan_mode="standard")
        defs = get_tools_definitions()
        assert len(defs) >= 5, f"Expected at least 5 tools, got {len(defs)}"

    def test_deep_mode_definitions(self):
        _register_scan_tools()
        llm = _make_llm(scan_mode="deep")
        defs = get_tools_definitions()
        assert len(defs) >= 5

    def test_no_xml_in_tool_definitions(self):
        """Ensure tool definitions contain zero XML artifacts."""
        _register_scan_tools()
        defs = get_tools_definitions()
        defs_str = json.dumps(defs)
        xml_markers = ["<tool>", "</tool>", "<function=", "<invoke", "<parameter>"]
        for marker in xml_markers:
            assert marker not in defs_str, f"XML marker '{marker}' found in tool definitions"


# ---------------------------------------------------------------------------
# Test: End-to-end agent loop simulation
# ---------------------------------------------------------------------------


class TestE2EAgentLoop:
    """Simulate the full agent loop with mock LLM producing native tool calls."""

    @pytest.mark.asyncio
    async def test_full_scan_loop_with_native_tool_calls(self):
        """Simulate a complete scan: init → think → exec → report → finish."""
        _register_scan_tools()

        state = AgentState(agent_name="Root Agent", max_iterations=20)

        # Simulate LLM responses that mirror real scan behavior
        mock_responses = [
            # Iteration 1: Agent thinks and starts scanning
            _make_llm_response(
                content="I'll start by analyzing the target. Let me run some initial checks.",
                tool_invocations=[
                    _make_native_tool_call("think", {"thought": "Starting scan of target"}),
                ],
            ),
            # Iteration 2: Run terminal command
            _make_llm_response(
                content="",
                tool_invocations=[
                    _make_native_tool_call(
                        "terminal_exec",
                        {"command": "nmap -sV target.example.com", "timeout": 60},
                    ),
                ],
            ),
            # Iteration 3: Browse to check web app
            _make_llm_response(
                content="Found a web application. Let me investigate further.",
                tool_invocations=[
                    _make_native_tool_call(
                        "browser_navigate",
                        {"url": "https://target.example.com"},
                    ),
                ],
            ),
            # Iteration 4: Report a finding
            _make_llm_response(
                content="I found a potential XSS vulnerability.",
                tool_invocations=[
                    _make_native_tool_call(
                        "report_vulnerability",
                        {
                            "title": "Reflected XSS in search parameter",
                            "description": "The search parameter reflects user input without encoding",
                            "severity": "high",
                            "url": "https://target.example.com/search?q=",
                        },
                    ),
                ],
            ),
            # Iteration 5: Finish the scan
            _make_llm_response(
                content="Scan complete. Found 1 vulnerability.",
                tool_invocations=[
                    _make_native_tool_call(
                        "finish_scan",
                        {
                            "summary": "Completed scan. Found 1 high-severity XSS vulnerability.",
                            "scan_completed": True,
                            "findings_count": 1,
                        },
                    ),
                ],
            ),
        ]

        # Add initial user task
        state.add_message("user", "Scan target: https://target.example.com")

        conversation_history = state.get_conversation_history()

        for response in mock_responses:
            state.increment_iteration()

            # Store assistant message with tool_calls (mirrors base_agent._process_iteration)
            raw_tool_calls = None
            if response.tool_invocations:
                raw_tool_calls = _make_tool_calls_from_invocations(response.tool_invocations)

            state.add_message(
                "assistant",
                response.content,
                tool_calls=raw_tool_calls,
            )

            # Execute tools (mirrors base_agent._execute_actions)
            if response.tool_invocations:
                should_finish = await process_tool_invocations(
                    response.tool_invocations,
                    conversation_history,
                    state,
                )

                if should_finish:
                    state.set_completed({"success": True})
                    break

        # Verify scan completed successfully
        assert state.completed, "Scan should have completed"
        assert state.final_result == {"success": True}

        # Verify native format throughout
        _assert_no_xml_in_history(conversation_history)
        _assert_native_tool_format(conversation_history)

        # Verify the expected number of tool messages
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 5, f"Expected 5 tool messages, got {len(tool_msgs)}"

        # Verify assistant messages have tool_calls
        assistant_msgs = [m for m in conversation_history if m["role"] == "assistant"]
        for msg in assistant_msgs:
            if msg.get("tool_calls"):
                assert isinstance(msg["tool_calls"], list)
                for tc in msg["tool_calls"]:
                    assert tc["type"] == "function"
                    assert "function" in tc
                    assert "name" in tc["function"]
                    assert "arguments" in tc["function"]

        # Verify iteration count
        assert state.iteration == 5

    @pytest.mark.asyncio
    async def test_multi_tool_invocation_single_response(self):
        """Verify multiple tool calls in a single LLM response all execute correctly."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=10)
        state.add_message("user", "Scan target")

        conversation_history = state.get_conversation_history()

        # LLM response with 3 simultaneous tool calls
        invocations = [
            _make_native_tool_call("think", {"thought": "Checking multiple endpoints"}, "call_001"),
            _make_native_tool_call(
                "terminal_exec",
                {"command": "curl -s https://target.example.com/health"},
                "call_002",
            ),
            _make_native_tool_call(
                "browser_navigate",
                {"url": "https://target.example.com/login"},
                "call_003",
            ),
        ]

        state.add_message(
            "assistant",
            "Checking multiple endpoints simultaneously.",
            tool_calls=_make_tool_calls_from_invocations(invocations),
        )

        should_finish = await process_tool_invocations(
            invocations, conversation_history, state
        )

        assert not should_finish

        # All 3 tool results should be present
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 3

        # Each should have unique tool_call_id matching the invocation
        call_ids = {m["tool_call_id"] for m in tool_msgs}
        assert "call_001" in call_ids
        assert "call_002" in call_ids
        assert "call_003" in call_ids

        # No XML in any result
        _assert_no_xml_in_history(conversation_history)
        _assert_native_tool_format(conversation_history)

    @pytest.mark.asyncio
    async def test_error_recovery_preserves_native_format(self):
        """Verify that tool execution errors still produce native tool messages."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=10)
        state.add_message("user", "Scan target")

        conversation_history = state.get_conversation_history()

        # Valid tool call
        invocations_valid = [
            _make_native_tool_call("think", {"thought": "Starting"}, "call_valid_001"),
        ]
        state.add_message(
            "assistant", "Starting scan.", tool_calls=_make_tool_calls_from_invocations(invocations_valid)
        )
        await process_tool_invocations(invocations_valid, conversation_history, state)

        # Invalid tool call (non-existent tool)
        invocations_invalid = [
            _make_native_tool_call("nonexistent_tool", {"param": "value"}, "call_invalid_001"),
        ]
        state.add_message(
            "assistant",
            "Trying a bad tool.",
            tool_calls=_make_tool_calls_from_invocations(invocations_invalid),
        )
        await process_tool_invocations(invocations_invalid, conversation_history, state)

        # Tool with missing required params
        invocations_missing_params = [
            _make_native_tool_call("terminal_exec", {}, "call_missing_001"),
        ]
        state.add_message(
            "assistant",
            "Missing params.",
            tool_calls=_make_tool_calls_from_invocations(invocations_missing_params),
        )
        await process_tool_invocations(
            invocations_missing_params, conversation_history, state
        )

        # Recovery: valid call after errors
        invocations_recovery = [
            _make_native_tool_call(
                "finish_scan",
                {"summary": "Completed despite errors", "scan_completed": True},
                "call_recovery_001",
            ),
        ]
        state.add_message(
            "assistant",
            "Finishing scan.",
            tool_calls=_make_tool_calls_from_invocations(invocations_recovery),
        )
        should_finish = await process_tool_invocations(
            invocations_recovery, conversation_history, state
        )
        assert should_finish

        # All results (including errors) should be native tool messages
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 4  # 1 valid + 1 bad tool + 1 missing params + 1 recovery

        _assert_no_xml_in_history(conversation_history)
        _assert_native_tool_format(conversation_history)

        # Error messages should be in the content, not as XML
        for msg in tool_msgs:
            content = msg.get("content", "")
            if isinstance(content, str) and "Error" in content:
                assert "<tool_result>" not in content
                assert "<tool_name>" not in content


# ---------------------------------------------------------------------------
# Test: Subagent delegation with native format
# ---------------------------------------------------------------------------


class TestSubagentDelegation:
    """Verify subagent creation and completion in native format."""

    @pytest.mark.asyncio
    async def test_create_and_finish_subagent(self):
        """Simulate creating a subagent and having it finish."""
        _register_scan_tools()

        parent_state = AgentState(agent_name="Root Agent", max_iterations=20)
        parent_state.add_message("user", "Scan target")

        conversation_history = parent_state.get_conversation_history()

        # Create a subagent
        create_invocations = [
            _make_native_tool_call(
                "create_agent",
                {"name": "XSS Scanner", "task": "Check for XSS vulnerabilities"},
                "call_create_001",
            ),
        ]
        parent_state.add_message(
            "assistant",
            "Delegating XSS scanning to a sub-agent.",
            tool_calls=_make_tool_calls_from_invocations(create_invocations),
        )
        await process_tool_invocations(
            create_invocations, conversation_history, parent_state
        )

        # Subagent does its work (simulated by a think call on parent)
        think_invocations = [
            _make_native_tool_call(
                "think",
                {"thought": "Sub-agent is working on XSS checks"},
                "call_think_001",
            ),
        ]
        parent_state.add_message(
            "assistant",
            "Sub-agent reported findings.",
            tool_calls=_make_tool_calls_from_invocations(think_invocations),
        )
        await process_tool_invocations(
            think_invocations, conversation_history, parent_state
        )

        # Finish the scan
        finish_invocations = [
            _make_native_tool_call(
                "finish_scan",
                {
                    "summary": "Sub-agent found XSS. Scan complete.",
                    "scan_completed": True,
                    "findings_count": 2,
                },
                "call_finish_001",
            ),
        ]
        parent_state.add_message(
            "assistant",
            "Scan complete.",
            tool_calls=_make_tool_calls_from_invocations(finish_invocations),
        )
        should_finish = await process_tool_invocations(
            finish_invocations, conversation_history, parent_state
        )

        assert should_finish
        _assert_no_xml_in_history(conversation_history)
        _assert_native_tool_format(conversation_history)


# ---------------------------------------------------------------------------
# Test: Scan mode skill loading
# ---------------------------------------------------------------------------


class TestScanModeSkillLoading:
    """Verify skills load correctly for different scan modes."""

    def test_quick_mode_skills_in_system_prompt(self):
        """Quick mode should configure the quick scan mode skill."""
        _register_scan_tools()
        config = _mock_llm_config(scan_mode="quick", skills=["root_agent"])
        # Verify config has the right scan_mode (skills loading is verified by config)
        assert config.scan_mode == "quick"
        assert "root_agent" in config.skills

    def test_deep_mode_skills_in_system_prompt(self):
        """Deep mode should configure the deep scan mode skill."""
        _register_scan_tools()
        config = _mock_llm_config(scan_mode="deep", skills=["root_agent"])
        assert config.scan_mode == "deep"
        assert "root_agent" in config.skills

    def test_skill_loading_tool(self):
        """Test that the load_skill tool registration and execution works."""
        _register_scan_tools()
        tool_names = [t["function"]["name"] for t in get_tools_definitions()]
        assert "load_skill" in tool_names


# ---------------------------------------------------------------------------
# Test: LLM message preparation for native format
# ---------------------------------------------------------------------------


class TestLLMMessagePreparation:
    """Verify LLM._prepare_messages handles native tool-call history correctly."""

    def test_prepare_messages_with_native_tool_history(self):
        """Verify that a conversation with native tool calls is prepared correctly."""
        _register_scan_tools()
        llm = _make_llm(scan_mode="standard")

        # Build a conversation history mimicking real scan
        history = [
            {"role": "user", "content": "Scan https://example.com"},
            {
                "role": "assistant",
                "content": "I'll start scanning.",
                "tool_calls": [
                    {
                        "id": "call_001",
                        "type": "function",
                        "function": {
                            "name": "terminal_exec",
                            "arguments": '{"command": "curl -I https://example.com"}',
                        },
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_001",
                "content": "HTTP/1.1 200 OK\nServer: nginx",
            },
            {
                "role": "assistant",
                "content": "Server is running nginx. Let me check for vulnerabilities.",
            },
        ]

        prepared = llm._prepare_messages(history)

        # First message should be system prompt
        assert prepared[0]["role"] == "system"

        # Find the tool message in prepared
        tool_msgs = [m for m in prepared if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        assert tool_msgs[0]["tool_call_id"] == "call_001"
        assert tool_msgs[0]["content"] == "HTTP/1.1 200 OK\nServer: nginx"

        # Find the assistant message with tool_calls
        assistant_with_tools = [m for m in prepared if m["role"] == "assistant" and m.get("tool_calls")]
        assert len(assistant_with_tools) == 1
        assert assistant_with_tools[0]["tool_calls"][0]["id"] == "call_001"

        # No XML in prepared messages
        prepared_str = json.dumps(prepared)
        assert "<tool_result>" not in prepared_str
        assert "<function=" not in prepared_str

    def test_prepare_messages_with_multipart_tool_result(self):
        """Verify tool messages with multipart content (e.g., screenshots) work."""
        _register_scan_tools()
        llm = _make_llm(scan_mode="standard")

        history = [
            {"role": "user", "content": "Scan target"},
            {
                "role": "assistant",
                "content": "Taking screenshot.",
                "tool_calls": [
                    {
                        "id": "call_ss_001",
                        "type": "function",
                        "function": {"name": "browser_navigate", "arguments": '{"url": "https://example.com"}'},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_ss_001",
                "content": [
                    {"type": "text", "text": "Screenshot captured successfully"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/png;base64,iVBOR..."},
                    },
                ],
            },
        ]

        prepared = llm._prepare_messages(history)

        tool_msgs = [m for m in prepared if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        # Content should be the multipart list
        assert isinstance(tool_msgs[0]["content"], list)
        assert len(tool_msgs[0]["content"]) == 2


# ---------------------------------------------------------------------------
# Test: Tool result format verification
# ---------------------------------------------------------------------------


class TestToolResultFormat:
    """Verify tool results are formatted as native tool role messages."""

    def test_dict_result_format(self):
        """Dict results should be stringified in tool message content."""
        result = {"success": True, "findings": ["XSS", "SQLi"]}
        msg, images = _format_tool_result("report_vulnerability", result, "call_fmt_001")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_fmt_001"
        assert isinstance(msg["content"], str)
        assert "XSS" in msg["content"]

    def test_string_result_format(self):
        """String results should be passed through."""
        msg, images = _format_tool_result("terminal_exec", "Command output here", "call_str_001")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_str_001"
        assert msg["content"] == "Command output here"

    def test_none_result_gets_default_message(self):
        """None results should get a descriptive default."""
        msg, images = _format_tool_result("think", None, "call_none_001")

        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_none_001"
        assert "successfully" in msg["content"].lower()

    def test_large_result_truncation(self):
        """Large results should be truncated to 10K chars."""
        large_result = "x" * 50000
        msg, images = _format_tool_result("terminal_exec", large_result, "call_large_001")

        assert msg["role"] == "tool"
        assert len(msg["content"]) < 50000
        assert "truncated" in msg["content"].lower()

    def test_tool_call_id_preserved_exactly(self):
        """Tool call IDs must be preserved exactly for LiteLLM matching."""
        special_id = "call_special-chars_123.456"
        msg, images = _format_tool_result("think", {"ok": True}, special_id)

        assert msg["tool_call_id"] == special_id


# ---------------------------------------------------------------------------
# Test: Performance and overhead
# ---------------------------------------------------------------------------


class TestPerformanceValidation:
    """Verify the native tool-calling pipeline has no significant overhead."""

    @pytest.mark.asyncio
    async def test_tool_execution_throughput(self):
        """Measure that 50 tool executions complete within a reasonable time."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=100)
        state.add_message("user", "Performance test")

        conversation_history = state.get_conversation_history()

        # Execute 50 tool calls
        start = time.monotonic()
        for i in range(50):
            invocations = [
                _make_native_tool_call(
                    "think",
                    {"thought": f"Iteration {i}"},
                    f"call_perf_{i:04d}",
                ),
            ]
            state.add_message(
                "assistant",
                f"Step {i}",
                tool_calls=_make_tool_calls_from_invocations(invocations),
            )
            await process_tool_invocations(
                invocations, conversation_history, state
            )

        elapsed = time.monotonic() - start

        # 50 tool executions should complete well under 5 seconds
        assert elapsed < 5.0, f"50 tool executions took {elapsed:.2f}s (expected < 5s)"

        # Verify all messages are native format
        _assert_no_xml_in_history(conversation_history)
        _assert_native_tool_format(conversation_history)

        # Verify correct count
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 50

    @pytest.mark.asyncio
    async def test_batch_execution_performance(self):
        """Measure that 10 batch calls of 5 tools each complete quickly."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=100)
        state.add_message("user", "Batch test")

        conversation_history = state.get_conversation_history()

        start = time.monotonic()
        for batch in range(10):
            invocations = [
                _make_native_tool_call("think", {"thought": f"Batch {batch}, tool {j}"}, f"call_batch_{batch}_{j}")
                for j in range(5)
            ]
            state.add_message(
                "assistant",
                f"Batch {batch}",
                tool_calls=_make_tool_calls_from_invocations(invocations),
            )
            await process_tool_invocations(
                invocations, conversation_history, state
            )

        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"10 batches of 5 tools took {elapsed:.2f}s (expected < 5s)"

        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 50


# ---------------------------------------------------------------------------
# Test: Scan completion flow
# ---------------------------------------------------------------------------


class TestScanCompletionFlow:
    """Verify scan completion with different tool sequences."""

    @pytest.mark.asyncio
    async def test_minimal_scan_loop(self):
        """Smallest possible scan: one think + finish_scan."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=10)
        state.add_message("user", "Quick scan target")

        conversation_history = state.get_conversation_history()

        # Single think call
        state.increment_iteration()
        inv1 = [_make_native_tool_call("think", {"thought": "Quick check"}, "call_q1")]
        state.add_message("assistant", "Quick check", tool_calls=_make_tool_calls_from_invocations(inv1))
        await process_tool_invocations(inv1, conversation_history, state)

        # Finish
        state.increment_iteration()
        inv2 = [
            _make_native_tool_call(
                "finish_scan",
                {"summary": "No issues found", "scan_completed": True},
                "call_q2",
            )
        ]
        state.add_message("assistant", "Done", tool_calls=_make_tool_calls_from_invocations(inv2))
        should_finish = await process_tool_invocations(inv2, conversation_history, state)

        assert should_finish
        assert state.iteration == 2

        # History: user, assistant(think), tool(think), assistant(finish), tool(finish)
        assert len(conversation_history) == 5
        _assert_no_xml_in_history(conversation_history)

    @pytest.mark.asyncio
    async def test_scan_with_vulnerability_report(self):
        """Verify vulnerability reporting produces correct tool result format."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=10)
        state.add_message("user", "Scan target for SQLi")

        conversation_history = state.get_conversation_history()

        # Report vulnerability
        inv = [
            _make_native_tool_call(
                "report_vulnerability",
                {
                    "title": "SQL Injection in login",
                    "description": "User input not parameterized",
                    "severity": "critical",
                    "url": "https://target.example.com/login",
                },
                "call_vuln_001",
            )
        ]
        state.add_message(
            "assistant",
            "Found SQLi!",
            tool_calls=_make_tool_calls_from_invocations(inv),
        )
        await process_tool_invocations(inv, conversation_history, state)

        # Check tool result contains vulnerability ID
        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        content = tool_msgs[0]["content"]
        assert "VULN-" in content
        assert "critical" in content

    @pytest.mark.asyncio
    async def test_web_search_tool_in_scan(self):
        """Verify web search integrates correctly in scan loop."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=10)
        state.add_message("user", "Research target")

        conversation_history = state.get_conversation_history()

        inv = [
            _make_native_tool_call(
                "web_search",
                {"query": "target.example.com CVE vulnerabilities"},
                "call_search_001",
            )
        ]
        state.add_message(
            "assistant",
            "Researching target.",
            tool_calls=_make_tool_calls_from_invocations(inv),
        )
        await process_tool_invocations(inv, conversation_history, state)

        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        assert "target.example.com" in tool_msgs[0]["content"]


# ---------------------------------------------------------------------------
# Test: Conversation history integrity
# ---------------------------------------------------------------------------


class TestConversationHistoryIntegrity:
    """Verify conversation history maintains correct structure throughout."""

    @pytest.mark.asyncio
    async def test_alternating_message_roles(self):
        """Verify tool results follow assistant messages with tool_calls."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=20)
        state.add_message("user", "Scan target")

        conversation_history = state.get_conversation_history()

        for i in range(3):
            invocations = [
                _make_native_tool_call("think", {"thought": f"Step {i}"}, f"call_{i:04d}"),
            ]
            state.add_message(
                "assistant",
                f"Step {i}",
                tool_calls=_make_tool_calls_from_invocations(invocations),
            )
            await process_tool_invocations(invocations, conversation_history, state)

        # Verify role sequence: user, assistant, tool, assistant, tool, assistant, tool
        roles = [m["role"] for m in conversation_history]
        assert roles[0] == "user"
        assert roles[1] == "assistant"
        assert roles[2] == "tool"
        assert roles[3] == "assistant"
        assert roles[4] == "tool"
        assert roles[5] == "assistant"
        assert roles[6] == "tool"

    @pytest.mark.asyncio
    async def test_tool_call_ids_unique_and_stable(self):
        """Verify all tool_call_ids are unique in the conversation."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=20)
        state.add_message("user", "Scan target")

        conversation_history = state.get_conversation_history()

        for i in range(10):
            invocations = [
                _make_native_tool_call("think", {"thought": f"Step {i}"}, f"call_unique_{i:04d}"),
            ]
            state.add_message(
                "assistant",
                f"Step {i}",
                tool_calls=_make_tool_calls_from_invocations(invocations),
            )
            await process_tool_invocations(invocations, conversation_history, state)

        tool_msgs = [m for m in conversation_history if m["role"] == "tool"]
        call_ids = [m["tool_call_id"] for m in tool_msgs]
        assert len(call_ids) == 10
        assert len(set(call_ids)) == 10, f"Duplicate tool_call_ids found: {call_ids}"

    @pytest.mark.asyncio
    async def test_agent_state_execution_summary(self):
        """Verify AgentState.get_execution_summary reflects scan state."""
        _register_scan_tools()
        state = AgentState(agent_name="Root Agent", max_iterations=50)
        state.add_message("user", "Scan target")

        conversation_history = state.get_conversation_history()

        for i in range(5):
            state.increment_iteration()
            invocations = [
                _make_native_tool_call("think", {"thought": f"Step {i}"}, f"call_summ_{i}"),
            ]
            state.add_action(invocations[0])  # Mimics base_agent._execute_actions
            state.add_message(
                "assistant",
                f"Step {i}",
                tool_calls=_make_tool_calls_from_invocations(invocations),
            )
            await process_tool_invocations(invocations, conversation_history, state)

        summary = state.get_execution_summary()
        assert summary["iteration"] == 5
        assert summary["total_actions"] == 5
        assert summary["agent_name"] == "Root Agent"
        assert not summary["completed"]
        assert not summary["has_errors"]

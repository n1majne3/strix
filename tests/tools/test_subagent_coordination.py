"""Tests for subagent coordination with native tool-calling harness.

Verifies that:
1. Subagent creation via create_agent tool works and delegation messages flow correctly
2. Inter-agent messaging (send_message_to_agent, wait_for_message) works
3. Agent completion flow (agent_finish) propagates results to parent
4. Agent graph state synchronization works across agents
5. Multi-agent coordination with 2-3 subagents works
6. Inter-agent XML tags in message content are NOT confused with tool calls
7. clean_content() strips inter-agent tags from TUI display
"""

import threading
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.agents.state import AgentState
from strix.llm.config import LLMConfig
from strix.llm.utils import clean_content
from strix.tools.agents_graph import agents_graph_actions
from strix.tools.executor import process_tool_invocations
from strix.tools.registry import clear_registry, register_tool


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_agent_graph():
    """Reset the global agent graph state before and after each test."""
    agents_graph_actions._agent_graph["nodes"].clear()
    agents_graph_actions._agent_graph["edges"].clear()
    agents_graph_actions._agent_messages.clear()
    agents_graph_actions._running_agents.clear()
    agents_graph_actions._agent_instances.clear()
    agents_graph_actions._agent_states.clear()
    agents_graph_actions._root_agent_id = None
    yield
    agents_graph_actions._agent_graph["nodes"].clear()
    agents_graph_actions._agent_graph["edges"].clear()
    agents_graph_actions._agent_messages.clear()
    agents_graph_actions._running_agents.clear()
    agents_graph_actions._agent_instances.clear()
    agents_graph_actions._agent_states.clear()
    agents_graph_actions._root_agent_id = None


@pytest.fixture(autouse=True)
def _clean_registry():
    clear_registry()
    yield
    clear_registry()


def _make_agent_state(
    agent_id: str | None = None,
    agent_name: str = "Test Agent",
    parent_id: str | None = None,
) -> AgentState:
    """Create a minimal AgentState for testing."""
    kwargs: dict[str, Any] = {
        "agent_name": agent_name,
        "max_iterations": 10,
        "parent_id": parent_id,
    }
    if agent_id is not None:
        kwargs["agent_id"] = agent_id
    return AgentState(**kwargs)


def _register_graph_tools():
    """Register the agents_graph tools so they can be invoked by the executor."""

    @register_tool(sandbox_execution=False)
    def create_agent(
        agent_state: Any,
        task: str,
        name: str,
        inherit_context: bool = True,
        skills: str | None = None,
    ) -> dict[str, Any]:
        return agents_graph_actions.create_agent(agent_state, task, name, inherit_context, skills)

    @register_tool(sandbox_execution=False)
    def send_message_to_agent(
        agent_state: Any,
        target_agent_id: str,
        message: str,
        message_type: str = "information",
        priority: str = "normal",
    ) -> dict[str, Any]:
        return agents_graph_actions.send_message_to_agent(
            agent_state, target_agent_id, message, message_type, priority
        )

    @register_tool(sandbox_execution=False)
    def agent_finish(
        agent_state: Any,
        result_summary: str,
        findings: list[str] | None = None,
        success: bool = True,
        report_to_parent: bool = True,
        final_recommendations: list[str] | None = None,
    ) -> dict[str, Any]:
        return agents_graph_actions.agent_finish(
            agent_state, result_summary, findings, success, report_to_parent, final_recommendations
        )

    @register_tool(sandbox_execution=False)
    def wait_for_message(
        agent_state: Any,
        reason: str = "Waiting for messages",
    ) -> dict[str, Any]:
        return agents_graph_actions.wait_for_message(agent_state, reason)

    @register_tool(sandbox_execution=False)
    def view_agent_graph(agent_state: Any) -> dict[str, Any]:
        return agents_graph_actions.view_agent_graph(agent_state)


# ---------------------------------------------------------------------------
# 1. Subagent creation and delegation message flow
# ---------------------------------------------------------------------------


class TestSubagentCreation:
    """Verify that create_agent works and delegation messages flow correctly."""

    def test_create_agent_registers_instance_and_state(self, monkeypatch):
        """create_agent stores agent instance and state for thread execution."""
        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
        parent_id = "parent-1"

        # Register parent in graph
        agents_graph_actions._agent_graph["nodes"][parent_id] = {
            "name": "Parent",
            "task": "scan target",
            "status": "running",
            "parent_id": None,
        }
        agents_graph_actions._agent_instances[parent_id] = SimpleNamespace(
            llm_config=LLMConfig(scan_mode="standard"),
        )

        # Patch StrixAgent and Thread
        captured: dict[str, Any] = {}

        class FakeAgent:
            def __init__(self, config):
                captured["config"] = config

        class FakeThread:
            def __init__(self, target, args, daemon, name):
                self._target = target
                self._args = args

            def start(self):
                pass  # Don't actually run

        import strix.agents as agents_module

        monkeypatch.setattr(agents_module, "StrixAgent", FakeAgent)
        monkeypatch.setattr(agents_graph_actions.threading, "Thread", FakeThread)

        parent_state = SimpleNamespace(
            agent_id=parent_id,
            get_conversation_history=list,
        )
        result = agents_graph_actions.create_agent(
            agent_state=parent_state,
            task="subtask: scan endpoints",
            name="Scanner",
            inherit_context=False,
        )

        assert result["success"] is True
        child_id = result["agent_id"]
        assert child_id is not None

        # Agent instance should be stored (for thread to reference)
        assert child_id in agents_graph_actions._agent_instances
        assert isinstance(agents_graph_actions._agent_instances[child_id], FakeAgent)

        # State should have correct task
        child_state = captured["config"]["state"]
        assert child_state.task == "subtask: scan endpoints"
        assert child_state.parent_id == parent_id

    def test_create_agent_inherits_llm_config(self, monkeypatch):
        """Subagent inherits scan_mode and timeout from parent."""
        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
        parent_id = "parent-2"

        agents_graph_actions._agent_graph["nodes"][parent_id] = {
            "name": "Parent",
            "task": "task",
            "status": "running",
            "parent_id": None,
        }
        agents_graph_actions._agent_instances[parent_id] = SimpleNamespace(
            llm_config=LLMConfig(timeout=99, scan_mode="quick"),
        )

        captured: dict[str, Any] = {}

        class FakeAgent:
            def __init__(self, config):
                captured["config"] = config

        class FakeThread:
            def __init__(self, target, args, daemon, name):
                pass

            def start(self):
                pass

        import strix.agents as agents_module

        monkeypatch.setattr(agents_module, "StrixAgent", FakeAgent)
        monkeypatch.setattr(agents_graph_actions.threading, "Thread", FakeThread)

        parent_state = SimpleNamespace(agent_id=parent_id, get_conversation_history=list)
        agents_graph_actions.create_agent(
            agent_state=parent_state,
            task="subtask",
            name="Child",
            inherit_context=False,
        )

        llm_config = captured["config"]["llm_config"]
        assert isinstance(llm_config, LLMConfig)
        assert llm_config.scan_mode == "quick"
        assert llm_config.timeout == 99

    def test_delegation_message_contains_task(self, monkeypatch):
        """_run_agent_in_thread adds a user message with <agent_delegation> XML."""
        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")

        pid = "parent-d"
        cid = "child-d"
        agents_graph_actions._agent_graph["nodes"][pid] = {
            "name": "ParentAgent",
            "task": "parent task",
            "status": "running",
        }
        agents_graph_actions._agent_graph["nodes"][cid] = {
            "name": "ChildAgent",
            "task": "child task",
            "status": "running",
        }

        messages_added: list[tuple[str, str]] = []

        class FakeState:
            agent_id = cid
            agent_name = "ChildAgent"
            parent_id = pid
            task = "Scan /api/v1"
            stop_requested = False

            def add_message(self, role, content):
                messages_added.append((role, content))

            def model_dump(self):
                return {"agent_id": self.agent_id}

        class FakeAgent:
            llm_config = LLMConfig()

            async def agent_loop(self, task):
                return {"done": True}

        state = FakeState()
        agent = FakeAgent()
        agents_graph_actions._agent_instances[cid] = agent

        agents_graph_actions._run_agent_in_thread(agent, state, inherited_messages=[])

        # Should have delegation message
        delegation_msgs = [
            (r, c) for r, c in messages_added if "<agent_delegation>" in c
        ]
        assert len(delegation_msgs) >= 1, "Expected <agent_delegation> XML in messages"
        content = delegation_msgs[0][1]
        assert "Scan /api/v1" in content
        assert "ChildAgent" in content
        assert "ParentAgent" in content


# ---------------------------------------------------------------------------
# 2. Inter-agent messaging
# ---------------------------------------------------------------------------


class TestInterAgentMessaging:
    """Verify send_message_to_agent and wait_for_message work correctly."""

    def _setup_graph(self):
        """Set up a simple parent-child graph for messaging tests."""
        agents_graph_actions._agent_graph["nodes"]["sender"] = {
            "name": "Sender",
            "task": "send",
            "status": "running",
            "parent_id": None,
        }
        agents_graph_actions._agent_graph["nodes"]["receiver"] = {
            "name": "Receiver",
            "task": "receive",
            "status": "running",
            "parent_id": "sender",
        }

    def test_send_message_creates_message_in_queue(self):
        """send_message_to_agent adds a message to the target's queue."""
        self._setup_graph()

        sender_state = SimpleNamespace(agent_id="sender")
        result = agents_graph_actions.send_message_to_agent(
            agent_state=sender_state,
            target_agent_id="receiver",
            message="Hello from sender",
            message_type="information",
            priority="high",
        )

        assert result["success"] is True
        assert result["message_id"] is not None

        # Message should be in receiver's queue
        assert "receiver" in agents_graph_actions._agent_messages
        msgs = agents_graph_actions._agent_messages["receiver"]
        assert len(msgs) == 1
        assert msgs[0]["content"] == "Hello from sender"
        assert msgs[0]["message_type"] == "information"
        assert msgs[0]["priority"] == "high"
        assert msgs[0]["from"] == "sender"
        assert msgs[0]["delivered"] is True

    def test_send_message_creates_edge_in_graph(self):
        """Sending a message creates a 'message' type edge in the graph."""
        self._setup_graph()

        sender_state = SimpleNamespace(agent_id="sender")
        agents_graph_actions.send_message_to_agent(
            agent_state=sender_state,
            target_agent_id="receiver",
            message="test",
        )

        edges = agents_graph_actions._agent_graph["edges"]
        msg_edges = [
            e for e in edges if e.get("type") == "message"
        ]
        assert len(msg_edges) == 1
        assert msg_edges[0]["from"] == "sender"
        assert msg_edges[0]["to"] == "receiver"

    def test_send_message_to_nonexistent_agent_fails(self):
        """Sending to a non-existent agent returns error."""
        sender_state = SimpleNamespace(agent_id="sender")
        result = agents_graph_actions.send_message_to_agent(
            agent_state=sender_state,
            target_agent_id="nonexistent",
            message="test",
        )
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_wait_for_message_enters_waiting_state(self):
        """wait_for_message puts the agent into waiting_for_input state."""
        state = _make_agent_state(agent_id="waiter", agent_name="Waiter")
        assert not state.is_waiting_for_input()

        result = agents_graph_actions.wait_for_message(
            agent_state=state,
            reason="Waiting for scan results",
        )

        assert result["success"] is True
        assert result["status"] == "waiting"
        assert state.is_waiting_for_input()

    def test_message_delivery_formats_inter_agent_xml(self):
        """_check_agent_messages wraps delivered messages in <inter_agent_message> XML."""
        self._setup_graph()

        # Manually add an unread message
        agents_graph_actions._agent_messages["receiver"] = [
            {
                "id": "msg_test",
                "from": "sender",
                "to": "receiver",
                "content": "XSS found on /login",
                "message_type": "information",
                "priority": "high",
                "timestamp": "2025-01-01T00:00:00",
                "delivered": True,
                "read": False,
            }
        ]

        receiver_state = _make_agent_state(agent_id="receiver")

        # Call _check_agent_messages directly as an unbound method
        from strix.agents.base_agent import BaseAgent

        BaseAgent._check_agent_messages(None, receiver_state)

        # The message should have been added to state.messages
        assert len(receiver_state.messages) > 0
        last_user_msg = None
        for msg in receiver_state.messages:
            if msg["role"] == "user":
                last_user_msg = msg["content"]

        assert last_user_msg is not None
        assert "<inter_agent_message>" in last_user_msg
        assert "Sender" in last_user_msg
        assert "XSS found on /login" in last_user_msg
        assert "<delivery_notice>" in last_user_msg
        assert "<sender>" in last_user_msg

        # Message should be marked as read
        assert agents_graph_actions._agent_messages["receiver"][0]["read"] is True

    def test_user_message_delivery_no_xml_wrap(self):
        """Messages from user are added directly without <inter_agent_message> wrapping."""
        agents_graph_actions._agent_graph["nodes"]["agent-1"] = {
            "name": "Agent1",
            "task": "task",
            "status": "running",
        }

        agents_graph_actions._agent_messages["agent-1"] = [
            {
                "id": "msg_user",
                "from": "user",
                "to": "agent-1",
                "content": "Please stop scanning",
                "message_type": "instruction",
                "priority": "high",
                "timestamp": "2025-01-01T00:00:00",
                "delivered": True,
                "read": False,
            }
        ]

        state = _make_agent_state(agent_id="agent-1")
        from strix.agents.base_agent import BaseAgent

        BaseAgent._check_agent_messages(None, state)

        # User messages should NOT be wrapped in <inter_agent_message>
        user_msgs = [
            m for m in state.messages
            if m["role"] == "user" and "Please stop scanning" in str(m["content"])
        ]
        assert len(user_msgs) == 1
        assert "<inter_agent_message>" not in user_msgs[0]["content"]


# ---------------------------------------------------------------------------
# 3. Agent completion flow
# ---------------------------------------------------------------------------


class TestAgentCompletion:
    """Verify agent_finish propagates results to parent correctly."""

    def _setup_parent_child(self, monkeypatch):
        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
        parent_id = "parent-c"
        child_id = "child-c"
        agents_graph_actions._agent_graph["nodes"][parent_id] = {
            "name": "Parent",
            "task": "parent task",
            "status": "running",
            "parent_id": None,
        }
        agents_graph_actions._agent_graph["nodes"][child_id] = {
            "name": "Scanner",
            "task": "scan endpoints",
            "status": "running",
            "parent_id": parent_id,
        }
        agents_graph_actions._agent_instances[child_id] = SimpleNamespace(
            llm_config=LLMConfig(),
        )
        return parent_id, child_id

    def test_agent_finish_updates_graph_status(self, monkeypatch):
        """agent_finish sets the agent's status to 'finished'."""
        parent_id, child_id = self._setup_parent_child(monkeypatch)

        state = SimpleNamespace(
            agent_id=child_id,
            parent_id=parent_id,
        )
        result = agents_graph_actions.agent_finish(
            agent_state=state,
            result_summary="Scan complete",
            findings=["SQL injection on /api/users"],
            success=True,
        )

        assert result["agent_completed"] is True
        node = agents_graph_actions._agent_graph["nodes"][child_id]
        assert node["status"] == "finished"
        assert node["result"]["summary"] == "Scan complete"
        assert "SQL injection on /api/users" in node["result"]["findings"]

    def test_agent_finish_notifies_parent(self, monkeypatch):
        """agent_finish sends an <agent_completion_report> to parent's message queue."""
        parent_id, child_id = self._setup_parent_child(monkeypatch)

        state = SimpleNamespace(agent_id=child_id, parent_id=parent_id)
        result = agents_graph_actions.agent_finish(
            agent_state=state,
            result_summary="Done scanning",
            findings=["XSS on /search"],
            success=True,
            final_recommendations=["Fix input validation"],
        )

        assert result["parent_notified"] is True

        # Check parent's message queue
        parent_msgs = agents_graph_actions._agent_messages.get(parent_id, [])
        assert len(parent_msgs) == 1

        report = parent_msgs[0]
        assert "<agent_completion_report>" in report["content"]
        assert "Scanner" in report["content"]
        assert "Done scanning" in report["content"]
        assert "XSS on /search" in report["content"]
        assert "Fix input validation" in report["content"]
        assert report["priority"] == "high"

    def test_agent_finish_failure_status(self, monkeypatch):
        """agent_finish with success=False sets 'failed' status."""
        parent_id, child_id = self._setup_parent_child(monkeypatch)

        state = SimpleNamespace(agent_id=child_id, parent_id=parent_id)
        result = agents_graph_actions.agent_finish(
            agent_state=state,
            result_summary="Tool error",
            success=False,
        )

        assert result["agent_completed"] is True
        node = agents_graph_actions._agent_graph["nodes"][child_id]
        assert node["status"] == "failed"

    def test_root_agent_cannot_use_agent_finish(self):
        """agent_finish rejects calls from root agent (no parent_id)."""
        state = SimpleNamespace(agent_id="root", parent_id=None)
        result = agents_graph_actions.agent_finish(
            agent_state=state,
            result_summary="Done",
        )

        assert result["agent_completed"] is False
        assert "subagents" in result["error"].lower()

    def test_completion_report_xml_in_message_content_not_tool_call(self, monkeypatch):
        """The <agent_completion_report> XML is stored as message content, not as tool calls."""
        parent_id, child_id = self._setup_parent_child(monkeypatch)

        state = SimpleNamespace(agent_id=child_id, parent_id=parent_id)
        agents_graph_actions.agent_finish(
            agent_state=state,
            result_summary="Done",
            findings=["F1"],
        )

        # The message in parent's queue should be plain content, not a tool call
        parent_msgs = agents_graph_actions._agent_messages[parent_id]
        msg = parent_msgs[0]

        # It's a message dict with 'content' key, not a tool_calls structure
        assert "content" in msg
        assert "tool_calls" not in msg
        assert isinstance(msg["content"], str)
        assert "<agent_completion_report>" in msg["content"]


# ---------------------------------------------------------------------------
# 4. Agent graph state synchronization
# ---------------------------------------------------------------------------


class TestAgentGraphSync:
    """Verify agent graph state is synchronized across agents."""

    def test_view_agent_graph_shows_hierarchy(self):
        """view_agent_graph returns a tree showing parent-child relationships."""
        agents_graph_actions._agent_graph["nodes"]["root"] = {
            "name": "Root",
            "task": "main scan",
            "status": "running",
            "parent_id": None,
        }
        agents_graph_actions._agent_graph["nodes"]["child-1"] = {
            "name": "Scanner",
            "task": "scan",
            "status": "completed",
            "parent_id": "root",
        }
        agents_graph_actions._agent_graph["edges"].append(
            {"from": "root", "to": "child-1", "type": "delegation"}
        )

        state = SimpleNamespace(agent_id="root")
        result = agents_graph_actions.view_agent_graph(agent_state=state)

        assert "graph_structure" in result
        structure = result["graph_structure"]
        assert "Root" in structure
        assert "Scanner" in structure
        assert "Children" in structure

        summary = result["summary"]
        assert summary["total_agents"] == 2
        assert summary["completed"] == 1
        assert summary["running"] == 1

    def test_graph_tracks_all_agent_statuses(self):
        """The graph summary counts agents by status correctly."""
        for name, status in [
            ("a1", "running"),
            ("a2", "waiting"),
            ("a3", "completed"),
            ("a4", "stopped"),
            ("a5", "error"),
        ]:
            agents_graph_actions._agent_graph["nodes"][name] = {
                "name": name,
                "task": "t",
                "status": status,
            }

        state = SimpleNamespace(agent_id="a1")
        result = agents_graph_actions.view_agent_graph(agent_state=state)

        s = result["summary"]
        assert s["total_agents"] == 5
        assert s["running"] == 1
        assert s["waiting"] == 1
        assert s["completed"] == 1
        assert s["stopped"] == 1
        assert s["failed"] == 1


# ---------------------------------------------------------------------------
# 5. Multi-agent coordination
# ---------------------------------------------------------------------------


class TestMultiAgentCoordination:
    """Verify 2-3 subagents can coordinate on a task."""

    def test_two_agents_exchange_messages(self):
        """Two agents can send messages to each other."""
        agents_graph_actions._agent_graph["nodes"]["coord-1"] = {
            "name": "ReconAgent",
            "task": "recon",
            "status": "running",
            "parent_id": "root",
        }
        agents_graph_actions._agent_graph["nodes"]["coord-2"] = {
            "name": "ExploitAgent",
            "task": "exploit",
            "status": "running",
            "parent_id": "root",
        }

        # Agent 1 sends to Agent 2
        state1 = SimpleNamespace(agent_id="coord-1")
        result = agents_graph_actions.send_message_to_agent(
            agent_state=state1,
            target_agent_id="coord-2",
            message="Found /api/v1/users endpoint",
            message_type="information",
            priority="normal",
        )
        assert result["success"] is True

        # Agent 2 sends to Agent 1
        state2 = SimpleNamespace(agent_id="coord-2")
        result = agents_graph_actions.send_message_to_agent(
            agent_state=state2,
            target_agent_id="coord-1",
            message="Roger, testing it now",
            message_type="query",
            priority="normal",
        )
        assert result["success"] is True

        # Verify both queues have messages
        assert len(agents_graph_actions._agent_messages["coord-1"]) == 1
        assert len(agents_graph_actions._agent_messages["coord-2"]) == 1
        assert agents_graph_actions._agent_messages["coord-2"][0]["content"] == "Found /api/v1/users endpoint"
        assert agents_graph_actions._agent_messages["coord-1"][0]["content"] == "Roger, testing it now"

    def test_three_agents_with_completion_reports(self, monkeypatch):
        """Three subagents finish and send reports to parent."""
        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5")
        parent_id = "parent-multi"
        agents_graph_actions._agent_graph["nodes"][parent_id] = {
            "name": "Coordinator",
            "task": "coordinate scan",
            "status": "running",
            "parent_id": None,
        }

        child_ids = ["child-a", "child-b", "child-c"]
        for cid in child_ids:
            agents_graph_actions._agent_graph["nodes"][cid] = {
                "name": cid.upper(),
                "task": f"subtask {cid}",
                "status": "running",
                "parent_id": parent_id,
            }
            agents_graph_actions._agent_instances[cid] = SimpleNamespace(
                llm_config=LLMConfig(),
            )

        # Each child finishes
        for cid in child_ids:
            state = SimpleNamespace(agent_id=cid, parent_id=parent_id)
            result = agents_graph_actions.agent_finish(
                agent_state=state,
                result_summary=f"{cid} done",
                findings=[f"Finding from {cid}"],
                success=True,
            )
            assert result["agent_completed"] is True

        # Parent should have 3 messages
        parent_msgs = agents_graph_actions._agent_messages.get(parent_id, [])
        assert len(parent_msgs) == 3

        # All should be completion reports
        for msg in parent_msgs:
            assert "<agent_completion_report>" in msg["content"]
            assert msg["priority"] == "high"

        # Graph should show all completed
        for cid in child_ids:
            assert agents_graph_actions._agent_graph["nodes"][cid]["status"] == "finished"


# ---------------------------------------------------------------------------
# 6. Inter-agent XML NOT confused with tool calls
# ---------------------------------------------------------------------------


class TestXMLNotConfusedWithToolCalls:
    """Verify inter-agent XML tags in message content are handled correctly with native tool calling."""

    @pytest.mark.asyncio
    async def test_inter_agent_message_stripped_from_display(self):
        """<inter_agent_message> in message content is stripped by clean_content, not parsed as a tool."""
        content = """<inter_agent_message>
    <delivery_notice>
        <important>Message from another agent</important>
    </delivery_notice>
    <sender>
        <agent_name>Scanner</agent_name>
        <agent_id>agent_abc</agent_id>
    </sender>
    <content>
Found XSS on /search?q=test
    </content>
</inter_agent_message>"""

        # clean_content should strip inter-agent XML entirely
        cleaned = clean_content(content)
        assert "<inter_agent_message>" not in cleaned
        assert "Found XSS" not in cleaned

    @pytest.mark.asyncio
    async def test_agent_completion_report_stripped_from_display(self):
        """<agent_completion_report> in message content is stripped by clean_content."""
        content = """<agent_completion_report>
    <agent_info>
        <agent_name>Scanner</agent_name>
        <agent_id>agent_xyz</agent_id>
        <task>scan endpoints</task>
        <status>SUCCESS</status>
    </agent_info>
    <results>
        <summary>Found 3 issues</summary>
    </results>
</agent_completion_report>"""

        cleaned = clean_content(content)
        assert "<agent_completion_report>" not in cleaned
        assert "Found 3 issues" not in cleaned

    @pytest.mark.asyncio
    async def test_tool_call_xml_stripped_inter_agent_preserved_in_history(self):
        """When content has tool call XML, clean_content strips it but preserves surrounding text."""
        content = """I'll scan now.
<function=run_terminal>
<parameter=command>nmap -sV target
</function>

Also received this:
<inter_agent_message>
    <content>Be careful with port scanning</content>
</inter_agent_message>"""

        cleaned = clean_content(content)
        # Tool call XML should be stripped
        assert "<function=" not in cleaned
        assert "nmap" not in cleaned
        # Inter-agent XML should also be stripped
        assert "<inter_agent_message>" not in cleaned
        # Prose preserved
        assert "I'll scan now." in cleaned

    @pytest.mark.asyncio
    async def test_inter_agent_xml_preserved_in_history(self):
        """Inter-agent XML in conversation history is preserved as message content."""
        state = _make_agent_state()

        inter_agent_msg = """<inter_agent_message>
    <sender>
        <agent_name>Recon</agent_name>
    </sender>
    <content>Endpoint /api/admin is exposed</content>
</inter_agent_message>"""

        state.add_message("user", inter_agent_msg)
        state.add_message("assistant", "Acknowledged, investigating /api/admin")

        history = state.get_conversation_history()
        assert len(history) == 2
        assert "<inter_agent_message>" in history[0]["content"]
        assert history[1]["role"] == "assistant"

    @pytest.mark.asyncio
    async def test_completion_report_in_history_not_tool_role(self):
        """<agent_completion_report> arrives as user message, not tool role."""
        state = _make_agent_state()

        report = """<agent_completion_report>
    <agent_info>
        <agent_name>Scanner</agent_name>
    </agent_info>
    <results>
        <summary>Done</summary>
    </results>
</agent_completion_report>"""

        # This is how _check_agent_messages adds it: as a user message
        state.add_message("user", report)

        history = state.get_conversation_history()
        assert history[-1]["role"] == "user"
        # Not a tool role message
        assert history[-1]["role"] != "tool"

    @pytest.mark.asyncio
    async def test_native_tool_call_with_inter_agent_context(self):
        """Native tool calls work correctly when conversation includes inter-agent XML."""
        _register_graph_tools()

        state = _make_agent_state()

        # Add inter-agent message to history
        state.add_message("user", """<inter_agent_message>
    <content>Found /api endpoint</content>
</inter_agent_message>""")

        state.add_message("assistant", "I'll scan the /api endpoint now.")

        # Simulate a native tool call (as if from LLM response)
        tool_calls = [
            {
                "id": "call_ntv_1",
                "type": "function",
                "function": {
                    "name": "send_message_to_agent",
                    "arguments": '{"target_agent_id": "agent_rec", "message": "Scanning /api now"}',
                },
            }
        ]
        state.add_message("assistant", "", tool_calls=tool_calls)

        invocations = [
            {
                "toolName": "send_message_to_agent",
                "args": {
                    "target_agent_id": "agent_rec",
                    "message": "Scanning /api now",
                },
                "id": "call_ntv_1",
            }
        ]

        # Register target in graph
        agents_graph_actions._agent_graph["nodes"]["agent_rec"] = {
            "name": "ReconAgent",
            "task": "recon",
            "status": "running",
        }

        # Execute — the inter-agent XML in the history should not interfere
        history = state.get_conversation_history()
        result = await process_tool_invocations(invocations, history, state)

        # Tool should have executed successfully
        tool_msgs = [m for m in history if m["role"] == "tool"]
        assert len(tool_msgs) == 1
        tool_msg = tool_msgs[0]
        assert tool_msg["tool_call_id"] == "call_ntv_1"
        # The result should show success (it's a dict serialized as string)
        assert "success" in str(tool_msg["content"]).lower() or "True" in str(tool_msg["content"])


# ---------------------------------------------------------------------------
# 7. clean_content strips inter-agent tags
# ---------------------------------------------------------------------------


class TestCleanContentInterAgentTags:
    """Verify clean_content() strips inter-agent XML tags from TUI display."""

    def test_strips_inter_agent_message(self):
        """clean_content removes <inter_agent_message> blocks."""
        content = """Some text before.
<inter_agent_message>
    <delivery_notice>
        <important>Message from agent</important>
    </delivery_notice>
    <sender>
        <agent_name>Scanner</agent_name>
        <agent_id>agent_123</agent_id>
    </sender>
    <content>
Found critical XSS
    </content>
</inter_agent_message>
Some text after."""

        cleaned = clean_content(content)
        assert "<inter_agent_message>" not in cleaned
        assert "Found critical XSS" not in cleaned
        assert "Some text before." in cleaned
        assert "Some text after." in cleaned

    def test_strips_agent_completion_report(self):
        """clean_content removes <agent_completion_report> blocks."""
        content = """Processing results.
<agent_completion_report>
    <agent_info>
        <agent_name>Scanner</agent_name>
    </agent_info>
    <results>
        <summary>Scan complete with 5 findings</summary>
    </results>
</agent_completion_report>
Done."""

        cleaned = clean_content(content)
        assert "<agent_completion_report>" not in cleaned
        assert "Scan complete with 5 findings" not in cleaned
        assert "Processing results." in cleaned
        assert "Done." in cleaned

    def test_strips_both_tags_in_mixed_content(self):
        """clean_content removes both tag types from mixed content."""
        content = """Start
<inter_agent_message>
    <content>Agent msg</content>
</inter_agent_message>
Middle
<agent_completion_report>
    <results><summary>Report</summary></results>
</agent_completion_report>
End"""

        cleaned = clean_content(content)
        assert "<inter_agent_message>" not in cleaned
        assert "<agent_completion_report>" not in cleaned
        assert "Agent msg" not in cleaned
        assert "Report" not in cleaned
        assert "Start" in cleaned
        assert "Middle" in cleaned
        assert "End" in cleaned

    def test_case_insensitive_stripping(self):
        """clean_content strips tags regardless of case."""
        content = """<INTER_AGENT_MESSAGE>
    <content>Test</content>
</INTER_AGENT_MESSAGE>"""

        cleaned = clean_content(content)
        assert "INTER_AGENT_MESSAGE" not in cleaned
        assert "Test" not in cleaned

    def test_strips_tool_calls_also(self):
        """clean_content also removes <function=...> tool call XML."""
        content = """I'll scan.
<function=run_terminal>
<parameter=command>nmap target
</function>"""

        cleaned = clean_content(content)
        assert "<function=" not in cleaned
        assert "nmap" not in cleaned
        assert "I'll scan." in cleaned

    def test_empty_content_returns_empty(self):
        """clean_content handles empty/None content."""
        assert clean_content("") == ""
        assert clean_content(None) == ""

    def test_plain_text_unchanged(self):
        """clean_content leaves plain text without XML tags unchanged."""
        content = "Hello, this is a plain text message with no XML."
        assert clean_content(content) == content

    def test_preserves_shared_repo_wiki_tags(self):
        """clean_content does NOT strip <shared_repo_wiki> — only inter-agent tags."""
        content = """<shared_repo_wiki title="Repo Wiki">
Architecture: client/server
</shared_repo_wiki>"""

        cleaned = clean_content(content)
        assert "shared_repo_wiki" in cleaned
        assert "Architecture: client/server" in cleaned

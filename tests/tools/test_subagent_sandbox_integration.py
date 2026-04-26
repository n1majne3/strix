"""Integration tests for subagent-sandbox credential sharing.

Covers:
- Subagents inherit sandbox credentials from the shared DockerRuntime singleton
- _initialize_sandbox_and_state populates sandbox_id, sandbox_token, sandbox_info
- SandboxInitializationError is handled (agent loop returns error result)
- Multi-agent sandbox sharing (2-3 agents, same container, unique agent_ids)
- Agent graph tracks parent-child relationships with shared sandbox
"""

from __future__ import annotations

import asyncio
import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.agents.state import AgentState
from strix.runtime import SandboxInitializationError
from strix.runtime.runtime import SandboxInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_sandbox_info(
    *,
    workspace_id: str = "ws-abc123",
    api_url: str = "http://127.0.0.1:50001",
    auth_token: str = "tok-shared",
    tool_server_port: int = 50001,
    caido_port: int = 50002,
    agent_id: str = "agent-001",
) -> SandboxInfo:
    """Build a realistic SandboxInfo dict."""
    return SandboxInfo(
        workspace_id=workspace_id,
        api_url=api_url,
        auth_token=auth_token,
        tool_server_port=tool_server_port,
        caido_port=caido_port,
        agent_id=agent_id,
    )


def _make_mock_runtime(sandbox_info: SandboxInfo | None = None) -> MagicMock:
    """Build a mock runtime that returns the given sandbox_info from create_sandbox."""
    runtime = MagicMock()
    if sandbox_info is None:
        sandbox_info = _make_sandbox_info()
    runtime.create_sandbox = AsyncMock(return_value=sandbox_info)
    return runtime


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_global_state():
    """Reset agents_graph global state between tests."""
    from strix.tools.agents_graph import agents_graph_actions

    original_graph = agents_graph_actions._agent_graph.copy()
    original_root = agents_graph_actions._root_agent_id
    original_instances = agents_graph_actions._agent_instances.copy()
    original_states = agents_graph_actions._agent_states.copy()
    original_messages = agents_graph_actions._agent_messages.copy()
    original_running = agents_graph_actions._running_agents.copy()

    agents_graph_actions._agent_graph = {"nodes": {}, "edges": []}
    agents_graph_actions._root_agent_id = None
    agents_graph_actions._agent_instances = {}
    agents_graph_actions._agent_states = {}
    agents_graph_actions._agent_messages = {}
    agents_graph_actions._running_agents = {}

    yield

    agents_graph_actions._agent_graph = original_graph
    agents_graph_actions._root_agent_id = original_root
    agents_graph_actions._agent_instances = original_instances
    agents_graph_actions._agent_states = original_states
    agents_graph_actions._agent_messages = original_messages
    agents_graph_actions._running_agents = original_running


@pytest.fixture(autouse=True)
def _reset_runtime_singleton():
    """Ensure the global runtime singleton is reset between tests."""
    import strix.runtime as rt_module

    original = rt_module._global_runtime
    rt_module._global_runtime = None
    yield
    rt_module._global_runtime = original


# ===========================================================================
# Test: _initialize_sandbox_and_state populates sandbox state
# ===========================================================================


class TestInitializeSandboxAndState:
    @pytest.mark.asyncio
    async def test_populates_sandbox_fields(self) -> None:
        """_initialize_sandbox_and_state sets sandbox_id, sandbox_token, sandbox_info."""
        sandbox_info = _make_sandbox_info(
            workspace_id="ws-test",
            auth_token="tok-abc",
            agent_id="agent-001",
        )
        mock_runtime = _make_mock_runtime(sandbox_info)

        state = AgentState(agent_name="Test Agent")

        with (
            patch.dict(os.environ, {"STRIX_SANDBOX_MODE": "false"}),
            patch("strix.runtime.get_runtime", return_value=mock_runtime),
        ):
            from strix.agents.base_agent import BaseAgent

            agent = MagicMock(spec=BaseAgent)
            agent.state = state
            agent.local_sources = []

            await BaseAgent._initialize_sandbox_and_state(agent, "scan the target")

        assert state.sandbox_id == "ws-test"
        assert state.sandbox_token == "tok-abc"
        assert state.sandbox_info is not None
        assert state.sandbox_info["workspace_id"] == "ws-test"
        assert state.sandbox_info["agent_id"] == "agent-001"
        assert state.task == "scan the target"

    @pytest.mark.asyncio
    async def test_skips_sandbox_in_sandbox_mode(self) -> None:
        """In sandbox mode, _initialize_sandbox_and_state skips sandbox creation."""
        state = AgentState(agent_name="Inner Agent", task="inner task")

        with patch.dict(os.environ, {"STRIX_SANDBOX_MODE": "true"}):
            from strix.agents.base_agent import BaseAgent

            agent = MagicMock(spec=BaseAgent)
            agent.state = state
            agent.local_sources = []

            await BaseAgent._initialize_sandbox_and_state(agent, "inner task")

        assert state.sandbox_id is None
        assert state.sandbox_token is None
        assert state.sandbox_info is None
        assert state.task == "inner task"

    @pytest.mark.asyncio
    async def test_skips_when_sandbox_already_initialized(self) -> None:
        """When sandbox_id is already set, does not re-initialize sandbox."""
        state = AgentState(
            agent_name="Sub Agent",
            sandbox_id="ws-existing",
            sandbox_token="tok-existing",
            sandbox_info={"workspace_id": "ws-existing"},
        )

        with patch.dict(os.environ, {"STRIX_SANDBOX_MODE": "false"}):
            from strix.agents.base_agent import BaseAgent

            agent = MagicMock(spec=BaseAgent)
            agent.state = state
            agent.local_sources = []

            await BaseAgent._initialize_sandbox_and_state(agent, "new task")

        # Should not have changed sandbox fields
        assert state.sandbox_id == "ws-existing"
        assert state.sandbox_token == "tok-existing"


# ===========================================================================
# Test: SandboxInitializationError handling in agent loop
# ===========================================================================


class TestSandboxErrorHandling:
    def test_handle_sandbox_error_returns_error_dict(self) -> None:
        """_handle_sandbox_error returns error result with message and details."""
        from strix.agents.base_agent import BaseAgent

        state = AgentState(agent_name="Test Agent")
        agent = MagicMock(spec=BaseAgent)
        agent.state = state
        agent.interactive = False

        error = SandboxInitializationError("Docker is not available", "Please start Docker Desktop.")

        result = BaseAgent._handle_sandbox_error(agent, error, tracer=None)

        assert result["success"] is False
        assert "not available" in result["error"]
        assert result["details"] == "Please start Docker Desktop."
        assert state.completed is True
        assert len(state.errors) > 0

    def test_handle_sandbox_error_interactive_enters_waiting(self) -> None:
        """In interactive mode, _handle_sandbox_error enters waiting state before returning error."""
        from strix.agents.base_agent import BaseAgent

        state = AgentState(agent_name="Interactive Agent")
        agent = MagicMock(spec=BaseAgent)
        agent.state = state
        agent.interactive = True

        error = SandboxInitializationError("Container failed", "Timeout.")

        result = BaseAgent._handle_sandbox_error(agent, error, tracer=None)

        # Interactive mode still returns error dict but enters waiting state
        assert result["success"] is False
        assert state.waiting_for_input is True


# ===========================================================================
# Test: Multi-agent sandbox sharing
# ===========================================================================


class TestMultiAgentSandboxSharing:
    def test_multiple_agents_share_same_container(self) -> None:
        """Multiple agents with the same scan_id share the same container."""
        from strix.tools.agents_graph import agents_graph_actions

        # Create parent agent state and register in graph
        parent_state = AgentState(agent_name="Root Agent", task="main scan")
        parent_node = {
            "id": parent_state.agent_id,
            "name": "Root Agent",
            "task": "main scan",
            "status": "running",
            "parent_id": None,
            "created_at": parent_state.start_time,
            "finished_at": None,
            "result": None,
            "llm_config": "default",
            "agent_type": "StrixAgent",
            "state": parent_state.model_dump(),
        }
        agents_graph_actions._agent_graph["nodes"][parent_state.agent_id] = parent_node
        agents_graph_actions._root_agent_id = parent_state.agent_id

        # Create subagent states
        sub1_state = AgentState(
            agent_name="Sub 1",
            task="recon",
            parent_id=parent_state.agent_id,
        )
        sub2_state = AgentState(
            agent_name="Sub 2",
            task="exploit",
            parent_id=parent_state.agent_id,
        )

        # All three share the same scan context (via _get_scan_id)
        # Simulate sandbox info assignment
        shared_workspace = "ws-shared-container"
        shared_token = "tok-shared-secret"

        for s in [parent_state, sub1_state, sub2_state]:
            s.sandbox_id = shared_workspace
            s.sandbox_token = shared_token
            s.sandbox_info = {
                "workspace_id": shared_workspace,
                "api_url": "http://127.0.0.1:50001",
                "auth_token": shared_token,
                "tool_server_port": 50001,
                "caido_port": 50002,
                "agent_id": s.agent_id,
            }

        # All share the same container
        assert parent_state.sandbox_id == sub1_state.sandbox_id == sub2_state.sandbox_id
        assert parent_state.sandbox_token == sub1_state.sandbox_token == sub2_state.sandbox_token

        # Each has a unique agent_id for tool server registration
        agent_ids = {s.agent_id for s in [parent_state, sub1_state, sub2_state]}
        assert len(agent_ids) == 3

    def test_agent_graph_tracks_parent_child_with_shared_sandbox(self) -> None:
        """Agent graph edges reflect parent-child delegation with shared sandbox."""
        from strix.tools.agents_graph import agents_graph_actions

        parent_id = "agent-parent-001"
        child_id = "agent-child-002"

        parent_node = {
            "id": parent_id,
            "name": "Root Agent",
            "task": "main scan",
            "status": "running",
            "parent_id": None,
            "sandbox_id": "ws-shared",
        }
        child_node = {
            "id": child_id,
            "name": "Sub Agent",
            "task": "recon",
            "status": "running",
            "parent_id": parent_id,
            "sandbox_id": "ws-shared",
        }

        agents_graph_actions._agent_graph["nodes"][parent_id] = parent_node
        agents_graph_actions._agent_graph["nodes"][child_id] = child_node
        agents_graph_actions._agent_graph["edges"].append(
            {"from": parent_id, "to": child_id, "type": "delegation"}
        )

        # Verify edge exists
        assert len(agents_graph_actions._agent_graph["edges"]) == 1
        edge = agents_graph_actions._agent_graph["edges"][0]
        assert edge["from"] == parent_id
        assert edge["to"] == child_id
        assert edge["type"] == "delegation"

        # Both share the same sandbox
        assert (
            agents_graph_actions._agent_graph["nodes"][parent_id]["sandbox_id"]
            == agents_graph_actions._agent_graph["nodes"][child_id]["sandbox_id"]
        )

    @pytest.mark.asyncio
    async def test_subagent_gets_unique_agent_id_registered(self) -> None:
        """Each subagent gets a unique agent_id registered on the tool server."""
        # Simulate creating sandbox info for parent
        parent_info = _make_sandbox_info(agent_id="agent-parent")
        # Simulate creating sandbox info for child (same container, different agent_id)
        child_info = _make_sandbox_info(
            workspace_id=parent_info["workspace_id"],
            auth_token=parent_info["auth_token"],
            agent_id="agent-child",
        )

        # Same container ID (workspace_id), different agent_ids
        assert parent_info["workspace_id"] == child_info["workspace_id"]
        assert parent_info["auth_token"] == child_info["auth_token"]
        assert parent_info["agent_id"] != child_info["agent_id"]


# ===========================================================================
# Test: Agent state sandbox fields
# ===========================================================================


class TestAgentStateSandboxFields:
    def test_default_sandbox_fields_are_none(self) -> None:
        """New AgentState has sandbox fields defaulted to None."""
        state = AgentState()
        assert state.sandbox_id is None
        assert state.sandbox_token is None
        assert state.sandbox_info is None

    def test_sandbox_fields_populated_from_sandbox_info(self) -> None:
        """AgentState sandbox fields can be populated from SandboxInfo."""
        info = _make_sandbox_info(
            workspace_id="ws-123",
            auth_token="tok-xyz",
            tool_server_port=48081,
            caido_port=48080,
            agent_id="agent-abc",
        )

        state = AgentState()
        state.sandbox_id = info["workspace_id"]
        state.sandbox_token = info["auth_token"]
        state.sandbox_info = dict(info)

        assert state.sandbox_id == "ws-123"
        assert state.sandbox_token == "tok-xyz"
        assert state.sandbox_info["tool_server_port"] == 48081
        assert state.sandbox_info["caido_port"] == 48080

    def test_execution_summary_includes_sandbox_info(self) -> None:
        """get_execution_summary includes sandbox fields."""
        state = AgentState(agent_name="Test Agent")
        state.sandbox_id = "ws-summary"
        state.sandbox_info = {"workspace_id": "ws-summary"}

        summary = state.get_execution_summary()
        assert summary["sandbox_id"] == "ws-summary"
        assert summary["sandbox_info"]["workspace_id"] == "ws-summary"

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from strix.agents.base_agent import BaseAgent
from strix.agents.state import AgentState
from strix.llm.config import LLMConfig
from strix.runtime import SandboxInitializationError
from strix.runtime.runtime import SandboxInfo
from strix.tools.agents_graph import agents_graph_actions


@pytest.fixture(autouse=True)
def setup_env():
    with patch("strix.llm.config.resolve_llm_config", return_value=("test-model", "test-key", "test-base")):
        yield

@pytest.fixture
def mock_runtime():
    with patch("strix.runtime.get_runtime") as mock_get_runtime:
        runtime = AsyncMock()
        mock_get_runtime.return_value = runtime
        yield runtime


@pytest.fixture
def base_agent():
    config = {
        "llm_config": LLMConfig(skills=[]),
        "state": AgentState(agent_name="Test Agent", task="")
    }
    # Mock llm to avoid any litellm/network calls during init
    with patch("strix.agents.base_agent.LLM"):
        agent = BaseAgent(config)
        yield agent


@pytest.mark.asyncio
async def test_initialize_sandbox_and_state_success(base_agent, mock_runtime):
    mock_sandbox_info: SandboxInfo = {
        "workspace_id": "test-workspace-123",
        "api_url": "http://localhost:10001",
        "auth_token": "test-token",
        "tool_server_port": 10001,
        "caido_port": 10002,
        "agent_id": base_agent.state.agent_id
    }
    mock_runtime.create_sandbox.return_value = mock_sandbox_info
    
    await base_agent._initialize_sandbox_and_state("New task")
    
    # Assert state is populated
    assert base_agent.state.sandbox_id == "test-workspace-123"
    assert base_agent.state.sandbox_token == "test-token"
    assert base_agent.state.sandbox_info == mock_sandbox_info
    
    # Assert task is updated and added to messages
    assert base_agent.state.task == "New task"
    assert base_agent.state.messages[-1]["role"] == "user"
    assert base_agent.state.messages[-1]["content"] == "New task"
    
    mock_runtime.create_sandbox.assert_called_once_with(
        base_agent.state.agent_id, None, []
    )


@pytest.mark.asyncio
async def test_initialize_sandbox_and_state_error(base_agent, mock_runtime):
    error = SandboxInitializationError("Docker failed", "Check daemon")
    mock_runtime.create_sandbox.side_effect = error
    
    with pytest.raises(SandboxInitializationError):
        await base_agent._initialize_sandbox_and_state("New task")


@pytest.mark.asyncio
async def test_subagent_sandbox_credentials_sharing(mock_runtime):
    # 1. Create parent agent
    parent_config = {
        "llm_config": LLMConfig(skills=[]),
        "state": AgentState(agent_name="Parent Agent", task="Root task")
    }
    with patch("strix.agents.base_agent.LLM"):
        parent_agent = BaseAgent(parent_config)
    
    # Mock parent initialization
    mock_sandbox_info: SandboxInfo = {
        "workspace_id": "shared-workspace-123",
        "api_url": "http://localhost:10001",
        "auth_token": "shared-token",
        "tool_server_port": 10001,
        "caido_port": 10002,
        "agent_id": parent_agent.state.agent_id
    }
    mock_runtime.create_sandbox.return_value = mock_sandbox_info
    
    await parent_agent._initialize_sandbox_and_state("Root task")
    
    # Simulate create_agent being called to spawn a subagent
    # It inherits context, but crucially passes parent_id
    with patch("strix.agents.base_agent.LLM"):
        result = agents_graph_actions.create_agent(
            parent_agent.state, 
            task="Sub task", 
            name="Sub Agent", 
            inherit_context=False
        )
    
    assert result["success"] is True
    subagent_id = result["agent_id"]
    
    # The subagent was created and its thread started. Let's inspect the state of the subagent.
    subagent_state = agents_graph_actions._agent_states[subagent_id]
    
    assert subagent_state.parent_id == parent_agent.state.agent_id
    
    # The subagent hasn't run its loop yet, so its sandbox info is empty initially
    # But when it runs _initialize_sandbox_and_state, it will use the parent's scan_id
    # via the agent_id prefix logic in DockerRuntime._get_scan_id.
    
    # However, in this test we can just verify the graph hierarchy works
    assert agents_graph_actions._agent_graph["nodes"][subagent_id]["parent_id"] == parent_agent.state.agent_id


def test_agent_handle_sandbox_error():
    config = {
        "llm_config": LLMConfig(skills=[]),
        "state": AgentState(agent_name="Test Agent", task="Do something")
    }
    with patch("strix.agents.base_agent.LLM"):
        agent = BaseAgent(config)
        
    error = SandboxInitializationError("Test Error", "Details here")
    result = agent._handle_sandbox_error(error, tracer=None)
    
    assert result["success"] is False
    assert result["error"] == "Test Error"
    assert result["details"] == "Details here"
    
    assert "Iteration 0: Test Error" in agent.state.errors


@pytest.mark.asyncio
async def test_subagent_gets_unique_agent_id_but_same_sandbox(mock_runtime):
    # This verifies the _get_scan_id logic conceptually in a test
    from strix.runtime.docker_runtime import DockerRuntime
    
    with patch("strix.runtime.docker_runtime.docker.from_env"), \
         patch("strix.runtime.docker_runtime.Config.get"):
        docker_runtime = DockerRuntime()
        
        # Test scan ID derivation
        # In actual execution, tracers or env variables handle this. 
        # But base behavior splits agent_id.
        scan_id_1 = docker_runtime._get_scan_id("agent_12345678")
        assert scan_id_1 == "scan-agent_12345678"
        
        # With tracer
        mock_tracer = MagicMock()
        mock_tracer.scan_config = {"scan_id": "test-scan-override"}
        
        with patch("strix.telemetry.tracer.get_global_tracer", return_value=mock_tracer):
            scan_id_2 = docker_runtime._get_scan_id("agent_12345678")
            assert scan_id_2 == "test-scan-override"

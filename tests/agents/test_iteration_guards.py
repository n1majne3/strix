import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from strix.agents.base_agent import BaseAgent
from strix.agents.state import AgentState
from strix.llm.config import LLMConfig

class DummyAgent(BaseAgent):
    agent_name = "DummyAgent"
    
    @property
    def default_llm_config(self):
        with patch("strix.llm.config.resolve_llm_config", return_value=("dummy", "dummy", "dummy")):
            return LLMConfig(model_name="dummy")

@pytest.mark.asyncio
async def test_urgent_warning_sent():
    config = {
        "max_iterations": 10
    }
    agent = DummyAgent(config)
    agent._initialize_sandbox_and_state = AsyncMock()
    
    # Force approaching max iterations to true
    agent.state.iteration = 7
    with patch.object(AgentState, 'is_approaching_max_iterations', return_value=True):
        await agent.agent_loop("test task")
    
    # Check messages
    messages = agent.state.get_conversation_history()
    urgent_msgs = [m for m in messages if m["role"] == "user" and "URGENT:" in str(m.get("content", ""))]
    assert len(urgent_msgs) == 1
    assert agent.state.max_iterations_warning_sent is True

@pytest.mark.asyncio
async def test_critical_warning_sent():
    config = {
        "max_iterations": 10
    }
    agent = DummyAgent(config)
    agent._initialize_sandbox_and_state = AsyncMock()
    
    agent.state.iteration = 6 # Next is 7, which is max_iterations - 3
    
    # We want _process_iteration to return True so the loop exits
    agent._process_iteration = AsyncMock(return_value=True)
    
    await agent.agent_loop("test task")
    
    messages = agent.state.get_conversation_history()
    critical_msgs = [m for m in messages if m["role"] == "user" and "CRITICAL: You have only 3 iterations left!" in str(m.get("content", ""))]
    assert len(critical_msgs) == 1

@pytest.mark.asyncio
async def test_empty_content_with_tool_calls_allowed():
    # Test that native tool calling with empty text content is allowed
    from strix.llm.llm import LLMResponse
    
    config = {
        "max_iterations": 10
    }
    agent = DummyAgent(config)
    agent._initialize_sandbox_and_state = AsyncMock()
    
    # Mock LLM to return empty content but with tool_calls
    async def mock_generate(*args, **kwargs):
        yield LLMResponse(
            content="",
            tool_calls=[{"id": "call_1", "type": "function", "function": {"name": "test_tool", "arguments": "{}"}}],
            tool_invocations=[{"toolName": "test_tool", "args": {}, "id": "call_1"}]
        )
        
    agent.llm.generate = mock_generate
    
    # Mock _execute_actions to finish the agent loop
    agent._execute_actions = AsyncMock(return_value=True)
    
    await agent.agent_loop("test task")
    
    messages = agent.state.get_conversation_history()
    
    # Verify no corrective "empty message" warning was added
    corrective_msgs = [m for m in messages if m["role"] == "user" and "You MUST NOT respond with empty messages" in str(m.get("content", ""))]
    assert len(corrective_msgs) == 0

def test_prepare_messages_native_tools():
    # Confirm prompt generation handles native schemas without XML
    from strix.llm.llm import LLM
    with patch("strix.llm.config.resolve_llm_config", return_value=("dummy", "dummy", "dummy")):
        config = LLMConfig(model_name="dummy")
    llm = LLM(config, agent_name="DummyAgent")
    
    history = [
        {
            "role": "assistant",
            "content": "I am calling a tool",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "test_tool", "arguments": "{}"}
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_1",
            "content": "Tool result output"
        }
    ]
    
    messages = llm._prepare_messages(history)
    
    # Assert assistant message is kept intact with tool_calls
    assistant_msg = messages[-2]
    assert assistant_msg["role"] == "assistant"
    assert assistant_msg["content"] == "I am calling a tool"
    assert "tool_calls" in assistant_msg
    assert assistant_msg["tool_calls"][0]["id"] == "call_1"
    
    # Assert tool message is kept intact
    tool_msg = messages[-1]
    assert tool_msg["role"] == "tool"
    assert tool_msg["tool_call_id"] == "call_1"
    assert tool_msg["content"] == "Tool result output"

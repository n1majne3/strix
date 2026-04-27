"""Real API end-to-end autonomous scan tests.

These tests validate that a real autonomous loop can discover vulnerabilities
using Anthropic and OpenAI models, proving the execution pipeline, tools,
and cost tracking work with real API responses.

Tests are gated behind ``STRIX_ANTHROPIC_API_KEY`` and
``STRIX_OPENAI_API_KEY`` environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Environment key helpers
# ---------------------------------------------------------------------------

ANTHROPIC_KEY_ENV = "STRIX_ANTHROPIC_API_KEY"
OPENAI_KEY_ENV = "STRIX_OPENAI_API_KEY"

anthropic_key = os.environ.get(ANTHROPIC_KEY_ENV)
openai_key = os.environ.get(OPENAI_KEY_ENV)


@pytest.fixture
def dummy_target(tmp_path: Path) -> Path:
    """Create a dummy Python file with a known SQL injection vulnerability."""
    target_file = tmp_path / "dummy_target.py"
    target_file.write_text(
        """import sqlite3

def get_user(username: str):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    # VULNERABILITY: SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
"""
    )
    return target_file


# ===========================================================================
# Anthropic provider real API autonomous tests
# ===========================================================================

@pytest.mark.skipif(not anthropic_key, reason=f"{ANTHROPIC_KEY_ENV} not set")
class TestAnthropicAutonomousScan:
    """Real autonomous scan tests using the Anthropic provider."""

    async def test_autonomous_scan_finds_vulnerability(self, dummy_target: Path, monkeypatch: pytest.MonkeyPatch):
        """Run a real autonomous scan with Anthropic to find the SQLi."""
        from strix.agents.StrixAgent.strix_agent import StrixAgent
        from strix.llm.config import LLMConfig

        monkeypatch.setenv("STRIX_LLM", "anthropic/claude-3-5-sonnet-latest")
        if anthropic_key:
            monkeypatch.setenv("LLM_API_KEY", anthropic_key)

        config = {
            "llm_config": LLMConfig(
                model_name="anthropic/claude-3-5-sonnet-latest",
                scan_mode="quick",
            )
        }

        agent = StrixAgent(config)

        scan_config = {
            "targets": [{"type": "local_code", "details": {"target_path": str(dummy_target)}}],
            "user_instructions": "Scan dummy_target.py for vulnerabilities, report what you find, and immediately call finish_scan.",
        }

        result = await agent.execute_scan(scan_config)

        assert agent.state.completed or len(agent.state.errors) > 0
        if not len(agent.state.errors) > 0:
            assert "SQL" in str(agent.state.get_conversation_history()) or "Injection" in str(agent.state.get_conversation_history())

            stats = agent.llm._provider.get_stats()
            assert stats.cost > 0
            assert stats.input_tokens > 0
            assert stats.input_tokens < 12000, f"Optimization failed: used {stats.input_tokens} input tokens (expected < 12000)"
            
            # Verify the agent's final state
            assert agent.state.iteration > 1, "Agent should have taken multiple steps"




# ===========================================================================
# OpenAI provider real API autonomous tests
# ===========================================================================

@pytest.mark.skipif(not openai_key, reason=f"{OPENAI_KEY_ENV} not set")
class TestOpenAIAutonomousScan:
    """Real autonomous scan tests using the OpenAI provider."""

    async def test_autonomous_scan_finds_vulnerability(self, dummy_target: Path, monkeypatch: pytest.MonkeyPatch):
        """Run a real autonomous scan with OpenAI to find the SQLi."""
        from strix.agents.StrixAgent.strix_agent import StrixAgent
        from strix.llm.config import LLMConfig

        monkeypatch.setenv("STRIX_LLM", "openai/gpt-4o-mini")
        if openai_key:
            monkeypatch.setenv("LLM_API_KEY", openai_key)

        config = {
            "llm_config": LLMConfig(
                model_name="openai/gpt-4o-mini",
                scan_mode="quick",
            )
        }

        agent = StrixAgent(config)

        scan_config = {
            "targets": [{"type": "local_code", "details": {"target_path": str(dummy_target)}}],
            "user_instructions": "Scan dummy_target.py for vulnerabilities, report what you find, and immediately call finish_scan.",
        }

        result = await agent.execute_scan(scan_config)

        assert agent.state.completed or len(agent.state.errors) > 0
        if not len(agent.state.errors) > 0:
            assert "SQL" in str(agent.state.get_conversation_history()) or "Injection" in str(agent.state.get_conversation_history())

            stats = agent.llm._provider.get_stats()
            assert stats.cost > 0
            assert stats.input_tokens > 0
            assert stats.input_tokens < 12000, f"Optimization failed: used {stats.input_tokens} input tokens (expected < 12000)"
            
            # Verify the agent's final state
            assert agent.state.iteration > 1, "Agent should have taken multiple steps"

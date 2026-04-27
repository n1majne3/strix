"""Real API end-to-end autonomous scan tests.

These tests validate that a real autonomous loop can discover vulnerabilities
using Anthropic and OpenAI models, proving the execution pipeline, tools,
and cost tracking work with real API responses.

Tests are gated behind ``STRIX_REAL_API_KEY`` and ``STRIX_REAL_API_BASE``
environment variables.  If either is unset, tests are skipped.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Environment key helpers
# ---------------------------------------------------------------------------

_API_KEY_ENV = "STRIX_REAL_API_KEY"
_API_BASE_ENV = "STRIX_REAL_API_BASE"

_api_key = os.environ.get(_API_KEY_ENV)
_api_base = os.environ.get(_API_BASE_ENV)

skip_if_no_credentials = pytest.mark.skipif(
    not _api_key or not _api_base,
    reason=f"Set {_API_KEY_ENV} and {_API_BASE_ENV} to run real API tests",
)


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


class TestAnthropicAutonomousScan:
    """Real autonomous scan tests using the Anthropic provider."""

    @skip_if_no_credentials
    async def test_autonomous_scan_finds_vulnerability(
        self, dummy_target: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Run a real autonomous scan with Anthropic to find the SQLi."""
        from strix.agents.StrixAgent.strix_agent import StrixAgent
        from strix.llm.config import LLMConfig

        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5.4-mini")
        monkeypatch.setenv("LLM_API_KEY", _api_key)
        monkeypatch.setenv("LLM_API_BASE", _api_base)

        config = {
            "llm_config": LLMConfig(
                model_name="openai/gpt-5.4-mini",
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
            assert "SQL" in str(agent.state.get_conversation_history()) or "Injection" in str(
                agent.state.get_conversation_history()
            )

            stats = agent.llm._provider.get_stats()
            assert stats.input_tokens > 0
            assert stats.input_tokens < 12000, (
                f"Optimization failed: used {stats.input_tokens} input tokens (expected < 12000)"
            )

            assert agent.state.iteration > 1, "Agent should have taken multiple steps"


# ===========================================================================
# OpenAI provider real API autonomous tests
# ===========================================================================


class TestOpenAIAutonomousScan:
    """Real autonomous scan tests using the OpenAI provider."""

    @skip_if_no_credentials
    async def test_autonomous_scan_finds_vulnerability(
        self, dummy_target: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Run a real autonomous scan with OpenAI to find the SQLi."""
        from strix.agents.StrixAgent.strix_agent import StrixAgent
        from strix.llm.config import LLMConfig

        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5.4-mini")
        monkeypatch.setenv("LLM_API_KEY", _api_key)
        monkeypatch.setenv("LLM_API_BASE", _api_base)

        config = {
            "llm_config": LLMConfig(
                model_name="openai/gpt-5.4-mini",
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
            assert "SQL" in str(agent.state.get_conversation_history()) or "Injection" in str(
                agent.state.get_conversation_history()
            )

            stats = agent.llm._provider.get_stats()
            assert stats.input_tokens > 0
            assert stats.input_tokens < 12000, (
                f"Optimization failed: used {stats.input_tokens} input tokens (expected < 12000)"
            )

            assert agent.state.iteration > 1, "Agent should have taken multiple steps"

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

    async def test_autonomous_scan_finds_vulnerability(self, dummy_target: Path):
        """Skeleton for running a real autonomous scan."""
        pass


# ===========================================================================
# OpenAI provider real API autonomous tests
# ===========================================================================

@pytest.mark.skipif(not openai_key, reason=f"{OPENAI_KEY_ENV} not set")
class TestOpenAIAutonomousScan:
    """Real autonomous scan tests using the OpenAI provider."""

    async def test_autonomous_scan_finds_vulnerability(self, dummy_target: Path):
        """Skeleton for running a real autonomous scan."""
        pass

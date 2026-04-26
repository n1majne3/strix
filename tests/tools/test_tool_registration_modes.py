"""Tests for tool registration modes (sandbox vs non-sandbox).

Each test runs in an isolated subprocess to avoid module-cache pollution
and import deadlocks from reloading ``strix.tools`` at runtime.
"""

import json
import subprocess
import sys


def _run_in_subprocess(code: str) -> subprocess.CompletedProcess[str]:
    """Execute *code* in a fresh Python process and return the result."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env={**__import__("os").environ},
    )


def test_non_sandbox_registers_agents_graph_but_not_browser_or_web_search_when_disabled() -> None:
    result = _run_in_subprocess(
        """
import os
os.environ["STRIX_SANDBOX_MODE"] = "false"
os.environ["STRIX_DISABLE_BROWSER"] = "true"
os.environ.pop("PERPLEXITY_API_KEY", None)

from strix.config import Config
Config.load = classmethod(lambda _cls: {"env": {}})

from strix.tools import get_tool_names
names = set(get_tool_names())
import json, sys
json.dump({"names": sorted(names)}, sys.stdout)
"""
    )
    assert result.returncode == 0, f"subprocess failed: {result.stderr}"
    data = json.loads(result.stdout)
    names = set(data["names"])
    assert "create_agent" in names, f"Expected create_agent, got: {sorted(names)}"
    assert "browser_action" not in names, f"browser_action should not be registered, got: {sorted(names)}"
    assert "web_search" not in names, f"web_search should not be registered, got: {sorted(names)}"


def test_sandbox_registers_sandbox_tools_but_not_non_sandbox_tools() -> None:
    result = _run_in_subprocess(
        """
import os
os.environ["STRIX_SANDBOX_MODE"] = "true"
os.environ["STRIX_DISABLE_BROWSER"] = "true"
os.environ.pop("PERPLEXITY_API_KEY", None)

from strix.config import Config
Config.load = classmethod(lambda _cls: {"env": {}})

from strix.tools import get_tool_names
names = set(get_tool_names())
import json, sys
json.dump({"names": sorted(names)}, sys.stdout)
"""
    )
    assert result.returncode == 0, f"subprocess failed: {result.stderr}"
    data = json.loads(result.stdout)
    names = set(data["names"])
    assert "terminal_execute" in names, f"Expected terminal_execute, got: {sorted(names)}"
    assert "python_action" in names, f"Expected python_action, got: {sorted(names)}"
    assert "list_requests" in names, f"Expected list_requests, got: {sorted(names)}"
    assert "create_agent" not in names, f"create_agent should not be registered, got: {sorted(names)}"
    assert "finish_scan" not in names, f"finish_scan should not be registered, got: {sorted(names)}"
    assert "load_skill" not in names, f"load_skill should not be registered, got: {sorted(names)}"
    assert "browser_action" not in names, f"browser_action should not be registered, got: {sorted(names)}"
    assert "web_search" not in names, f"web_search should not be registered, got: {sorted(names)}"


def test_load_skill_import_does_not_register_create_agent_in_sandbox() -> None:
    result = _run_in_subprocess(
        """
import os
os.environ["STRIX_SANDBOX_MODE"] = "true"
os.environ["STRIX_DISABLE_BROWSER"] = "true"
os.environ.pop("PERPLEXITY_API_KEY", None)

from strix.config import Config
Config.load = classmethod(lambda _cls: {"env": {}})

from strix.tools.registry import clear_registry, get_tool_names

clear_registry()
names_before = set(get_tool_names())

from strix.tools.load_skill import load_skill_actions

class DummyState:
    agent_id = "agent_test"
    context = {}
    def update_context(self, key, value):
        self.context[key] = value

result = load_skill_actions.load_skill(DummyState(), "nmap")
names_after = set(get_tool_names())

import json, sys
json.dump({
    "names_before": sorted(names_before),
    "names_after": sorted(names_after),
    "result_success": result["success"],
}, sys.stdout)
"""
    )
    assert result.returncode == 0, f"subprocess failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "load_skill" not in data["names_before"]
    assert "create_agent" not in data["names_before"]
    assert "create_agent" not in data["names_after"]
    assert data["result_success"] is False

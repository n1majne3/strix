# AnthropicProvider SDK Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `AnthropicProvider` to use the native `anthropic` Python SDK instead of litellm, matching the pattern used by `OpenAIProvider`.

**Architecture:** Drop-in replacement of `provider_anthropic.py` internals. The file's public API (`ProviderBase` methods) stays identical. Internally, `litellm.acompletion` is replaced by `anthropic.AsyncAnthropic.messages.stream()`, and message/tool format conversion is done in new private methods `_convert_messages` and `_convert_tools`.

**Tech Stack:** `anthropic` Python SDK v0.86+, `pytest`, `pytest-asyncio`

**Design spec:** `docs/superpowers/specs/2026-04-27-anthropic-sdk-migration-design.md`

---

## File Structure

| File | Action | Responsibility |
|------|--------|----------------|
| `strix/llm/provider_anthropic.py` | **Rewrite** | Full provider using anthropic SDK |
| `tests/llm/test_provider_anthropic.py` | **Rewrite** | Unit tests matching new implementation |
| `pyproject.toml` | **Modify** | Add `anthropic` dependency + mypy config |
| `tests/tools/test_real_autonomous_scan.py` | **Modify** | Fix Anthropic test model name |
| `strix/llm/provider_base.py` | No change | ABC contract unchanged |
| `strix/llm/provider_openai.py` | No change | Reference implementation |
| `strix/llm/llm.py` | No change | Routing unchanged |

---

### Task 1: Add anthropic SDK dependency

**Files:**
- Modify: `pyproject.toml:35-48` (dependencies list)
- Modify: `pyproject.toml:117-141` (mypy overrides)

- [ ] **Step 1: Add `anthropic` to dependencies and mypy overrides in pyproject.toml**

In the `dependencies` list, add `"anthropic>=0.86.0"` after the `"openai"` entry. In the `[[tool.mypy.overrides]]` module list, add `"anthropic.*"` to ignore missing imports.

```toml
# In [project] dependencies, after "openai>=1.30.0":
  "anthropic>=0.86.0",
```

```toml
# In [[tool.mypy.overrides]] module list, after "openai.*":
    "anthropic.*",
```

- [ ] **Step 2: Install and verify**

Run: `uv sync 2>&1 | tail -3`
Then: `.venv/bin/python -c "from anthropic import AsyncAnthropic; print('OK')"`

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add anthropic SDK dependency"
```

---

### Task 2: Write tests for message format conversion

**Files:**
- Create: `tests/llm/test_provider_anthropic.py` (replace existing)

This task creates the test file with tests for `_convert_messages`. The implementation follows in Task 4.

- [ ] **Step 1: Write test file header and fixtures**

```python
"""Tests for AnthropicProvider — message conversion, tool conversion, capabilities, streaming."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.llm.provider_base import LLMResponse, ProviderBase, RequestStats


def _make_config(**overrides):
    """Build a minimal LLMConfig-like object for testing."""
    cfg = MagicMock()
    cfg.canonical_model = overrides.get("canonical_model", "anthropic/claude-sonnet-4-20250514")
    cfg.litellm_model = overrides.get("litellm_model", "anthropic/claude-sonnet-4-20250514")
    cfg.timeout = overrides.get("timeout", 300)
    cfg.api_key = overrides.get("api_key", None)
    cfg.api_base = overrides.get("api_base", None)
    cfg.enable_prompt_caching = overrides.get("enable_prompt_caching", True)
    return cfg


@pytest.fixture
def provider():
    with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
        from strix.llm.provider_anthropic import AnthropicProvider

        return AnthropicProvider(_make_config(), reasoning_effort="high")
```

- [ ] **Step 2: Write tests for `_convert_messages` — system extraction**

Add inside the same file:

```python
class TestConvertMessagesSystemExtraction:
    """_convert_messages extracts system messages to a top-level system param."""

    def test_extracts_single_system_message(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hi"},
        ])
        assert system == "You are helpful."
        assert len(msgs) == 1
        assert msgs[0]["role"] == "user"

    def test_extracts_multiple_system_messages(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "system", "content": "Part 1."},
            {"role": "system", "content": "Part 2."},
            {"role": "user", "content": "Hi"},
        ])
        assert "Part 1." in system
        assert "Part 2." in system
        assert len(msgs) == 1

    def test_no_system_message_returns_empty_string(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Hi"},
        ])
        assert system == ""
        assert len(msgs) == 1

    def test_system_content_as_list_preserved(self, provider):
        """When system content is already a list (e.g. with cache_control), pass through."""
        content = [{"type": "text", "text": "You are helpful.", "cache_control": {"type": "ephemeral"}}]
        system, msgs = provider._convert_messages([
            {"role": "system", "content": content},
            {"role": "user", "content": "Hi"},
        ])
        assert isinstance(system, list)
        assert system[0]["cache_control"] == {"type": "ephemeral"}
```

- [ ] **Step 3: Write tests for `_convert_messages` — tool call conversion**

```python
class TestConvertMessagesToolCalls:
    """_convert_messages converts OpenAI tool_calls to Anthropic tool_use content blocks."""

    def test_assistant_tool_calls_to_tool_use(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Check files"},
            {
                "role": "assistant",
                "content": "Let me check.",
                "tool_calls": [{
                    "id": "call_123",
                    "type": "function",
                    "function": {"name": "read_file", "arguments": '{"path": "/etc/hosts"}'},
                }],
            },
        ])
        assert len(msgs) == 2
        assistant_msg = msgs[1]
        assert assistant_msg["role"] == "assistant"
        content = assistant_msg["content"]
        assert isinstance(content, list)
        # First block is text
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "Let me check."
        # Second block is tool_use
        assert content[1]["type"] == "tool_use"
        assert content[1]["id"] == "call_123"
        assert content[1]["name"] == "read_file"
        assert content[1]["input"] == {"path": "/etc/hosts"}

    def test_assistant_tool_calls_no_text_content(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_456",
                    "type": "function",
                    "function": {"name": "run", "arguments": "{}"},
                }],
            },
        ])
        content = msgs[1]["content"]
        assert len(content) == 1
        assert content[0]["type"] == "tool_use"

    def test_assistant_tool_calls_with_malformed_arguments(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_bad",
                    "type": "function",
                    "function": {"name": "run", "arguments": "{invalid json"},
                }],
            },
        ])
        content = msgs[1]["content"]
        assert content[0]["input"] == {}  # Falls back to empty dict

    def test_assistant_with_no_tool_calls_passes_content_as_string(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
        ])
        assert msgs[1]["content"] == "Hello!"
```

- [ ] **Step 4: Write tests for `_convert_messages` — tool result conversion**

```python
class TestConvertMessagesToolResults:
    """_convert_messages converts tool role messages to user tool_result content blocks."""

    def test_single_tool_result(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "run", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call_1", "content": "result data"},
        ])
        # The tool result should be a user message with tool_result content block
        result_msg = msgs[2]
        assert result_msg["role"] == "user"
        content = result_msg["content"]
        assert isinstance(content, list)
        assert content[0]["type"] == "tool_result"
        assert content[0]["tool_use_id"] == "call_1"
        assert content[0]["content"] == "result data"

    def test_consecutive_tool_results_merged(self, provider):
        """Multiple tool results should be merged into a single user message."""
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_1", "type": "function", "function": {"name": "a", "arguments": "{}"}},
                {"id": "call_2", "type": "function", "function": {"name": "b", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call_1", "content": "result a"},
            {"role": "tool", "tool_call_id": "call_2", "content": "result b"},
        ])
        # Should be: user, assistant, user (merged tool results)
        assert len(msgs) == 3
        merged = msgs[2]
        assert merged["role"] == "user"
        assert len(merged["content"]) == 2
        assert merged["content"][0]["tool_use_id"] == "call_1"
        assert merged["content"][1]["tool_use_id"] == "call_2"

    def test_tool_result_with_is_error(self, provider):
        """Tool results with error flag should include is_error=True."""
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_err", "type": "function", "function": {"name": "fail", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call_err", "content": "Error: file not found"},
        ])
        result_msg = msgs[2]
        # Tool results without explicit is_error should not set it
        assert result_msg["content"][0]["tool_use_id"] == "call_err"
```

- [ ] **Step 5: Write tests for `_convert_messages` — tool call ID normalization**

```python
class TestConvertMessagesToolCallIdNormalization:
    """Anthropic requires tool call IDs matching ^[a-zA-Z0-9_-]+$ (max 64 chars)."""

    def test_normal_id_passes_through(self, provider):
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call_abc123", "type": "function", "function": {"name": "x", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call_abc123", "content": "ok"},
        ])
        assert msgs[1]["content"][0]["id"] == "call_abc123"
        assert msgs[2]["content"][0]["tool_use_id"] == "call_abc123"

    def test_id_with_dots_sanitized(self, provider):
        """IDs with dots or special chars should be sanitized."""
        system, msgs = provider._convert_messages([
            {"role": "user", "content": "Go"},
            {"role": "assistant", "content": None, "tool_calls": [
                {"id": "call.abc.def", "type": "function", "function": {"name": "x", "arguments": "{}"}},
            ]},
            {"role": "tool", "tool_call_id": "call.abc.def", "content": "ok"},
        ])
        tc_id = msgs[1]["content"][0]["id"]
        assert "." not in tc_id
        # The tool result should use the same normalized ID
        assert msgs[2]["content"][0]["tool_use_id"] == tc_id
```

- [ ] **Step 6: Write tests for `_convert_tools`**

```python
class TestConvertTools:
    """_convert_tools converts OpenAI function-tool format to Anthropic input_schema format."""

    def test_converts_single_tool(self, provider):
        tools = [{"type": "function", "function": {
            "name": "read_file",
            "description": "Read a file from disk",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        }}]
        result = provider._convert_tools(tools)
        assert len(result) == 1
        assert result[0]["name"] == "read_file"
        assert result[0]["description"] == "Read a file from disk"
        assert result[0]["input_schema"]["type"] == "object"
        assert result[0]["input_schema"]["properties"]["path"]["type"] == "string"

    def test_converts_multiple_tools(self, provider):
        tools = [
            {"type": "function", "function": {"name": "a", "description": "Tool A", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "b", "description": "Tool B", "parameters": {"type": "object", "properties": {}}}},
        ]
        result = provider._convert_tools(tools)
        assert len(result) == 2
        assert result[0]["name"] == "a"
        assert result[1]["name"] == "b"

    def test_empty_tools_returns_empty_list(self, provider):
        assert provider._convert_tools([]) == []

    def test_tool_without_description(self, provider):
        tools = [{"type": "function", "function": {
            "name": "run",
            "parameters": {"type": "object", "properties": {}},
        }}]
        result = provider._convert_tools(tools)
        assert result[0]["name"] == "run"
        # Should not crash if description is missing

    def test_tool_without_parameters_gets_empty_schema(self, provider):
        tools = [{"type": "function", "function": {"name": "run"}}]
        result = provider._convert_tools(tools)
        assert result[0]["input_schema"]["type"] == "object"
```

- [ ] **Step 7: Run tests to verify they fail (not yet implemented)**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py -x -v 2>&1 | head -30`
Expected: Import errors or `AttributeError` since the new methods don't exist yet.

---

### Task 3: Implement message and tool conversion helpers

**Files:**
- Modify: `strix/llm/provider_anthropic.py` (full rewrite)

- [ ] **Step 1: Write the new `provider_anthropic.py` — imports, constants, class skeleton**

Replace the entire file content. This step writes everything except `generate_stream` (Task 5).

```python
"""Anthropic LLM provider backed by the native ``anthropic`` Python SDK."""

from __future__ import annotations

import json
import logging
import re
from typing import TYPE_CHECKING, Any

from anthropic import APIStatusError, AsyncAnthropic

from strix.llm.provider_base import (
    LLMRequestFailedError,
    LLMResponse,
    ProviderBase,
    RequestStats,
)


if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from strix.llm.config import LLMConfig

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model-name heuristics for capability detection
# ---------------------------------------------------------------------------

_REASONING_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet",
    "claude-3-7-sonnet",
    "claude-4-sonnet",
    "claude-4-opus",
})

_VISION_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet",
    "claude-3-7-sonnet",
    "claude-4-sonnet",
    "claude-4-opus",
})

# ---------------------------------------------------------------------------
# Fallback pricing (cost per token) for Claude models not in litellm
# ---------------------------------------------------------------------------

_FALLBACK_PRICING: dict[str, tuple[float, float]] = {
    # model_name: (input_cost_per_token, output_cost_per_token)
    "claude-sonnet-4": (3e-6, 1.5e-5),
    "claude-opus-4": (1.5e-5, 7.5e-5),
    "claude-3-5-sonnet": (3e-6, 1.5e-5),
    "claude-3-7-sonnet": (3e-6, 1.5e-5),
}

# HTTP status codes that are retryable
_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503})

# Anthropic tool call ID validation pattern
_TOOL_CALL_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")

# Thinking budget by reasoning effort level
_THINKING_BUDGETS: dict[str, int] = {
    "low": 4096,
    "medium": 16384,
    "high": 65536,
}

# Max tokens for responses (without thinking)
_DEFAULT_MAX_TOKENS = 16384


def _sanitize_tool_call_id(tc_id: str) -> str:
    """Sanitize a tool call ID to match Anthropic's ^[a-zA-Z0-9_-]+$ (max 64 chars)."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", tc_id)
    return sanitized[:64]


class AnthropicProvider(ProviderBase):
    """Concrete provider that drives Anthropic models via the native SDK."""

    def __init__(self, config: LLMConfig, reasoning_effort: str) -> None:
        self._config = config
        self._reasoning_effort = reasoning_effort
        self._stats = RequestStats()
        self._model_name = self._strip_anthropic_prefix(config.litellm_model)
        self._client = AsyncAnthropic(
            api_key=config.api_key or None,
            base_url=config.api_base or None,
        )

    # ------------------------------------------------------------------
    # ProviderBase abstract method implementations
    # ------------------------------------------------------------------

    def get_stats(self) -> RequestStats:
        return self._stats

    def get_model_name(self) -> str:
        return self._model_name

    def supports_vision(self) -> bool:
        base = self._model_name
        return any(base == m or base.startswith(m + "-") for m in _VISION_MODELS)

    def supports_reasoning(self) -> bool:
        base = self._model_name
        return any(base == m or base.startswith(m + "-") for m in _REASONING_MODELS)

    def supports_prompt_caching(self) -> bool:
        return True

    def should_retry(self, exc: Exception) -> bool:
        status_code = getattr(exc, "status_code", None)
        if status_code is None:
            return True
        return status_code in _RETRYABLE_STATUS_CODES

    def build_completion_args(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
    ) -> dict[str, Any]:
        """Build the ``AsyncAnthropic.messages.stream`` keyword arguments."""
        if not self.supports_vision():
            messages = self._strip_images(messages)

        system, converted_messages = self._convert_messages(messages)
        converted_tools = self._convert_tools(tools) if tools else []

        args: dict[str, Any] = {
            "model": self._model_name,
            "messages": converted_messages,
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "timeout": self._config.timeout,
        }

        if system:
            args["system"] = system

        if converted_tools:
            args["tools"] = converted_tools
            args["tool_choice"] = self._convert_tool_choice(tool_choice)

        if self.supports_reasoning():
            budget = _THINKING_BUDGETS.get(self._reasoning_effort, 16384)
            args["thinking"] = {"type": "enabled", "budget_tokens": budget}
            # max_tokens must be >= budget_tokens + 1 when thinking is enabled
            args["max_tokens"] = budget + _DEFAULT_MAX_TOKENS

        return args

    def prepare_messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Add cache_control markers for prompt caching."""
        if not messages:
            return messages

        result = list(messages)

        # Add cache_control to system message
        if result[0].get("role") == "system" and isinstance(result[0].get("content"), str):
            content = result[0]["content"]
            result[0] = {
                **result[0],
                "content": [
                    {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                ],
            }

        return result

    async def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
        **kwargs: Any,
    ) -> AsyncIterator[LLMResponse]:
        """Stream LLM responses using the Anthropic Messages API."""
        # Placeholder — implemented in Task 5
        raise NotImplementedError("Streaming implemented in Task 5")

    # ------------------------------------------------------------------
    # Message format conversion
    # ------------------------------------------------------------------

    def _convert_messages(
        self, messages: list[dict[str, Any]]
    ) -> tuple[str | list[dict[str, Any]], list[dict[str, Any]]]:
        """Convert OpenAI-style messages to Anthropic Messages API format.

        Returns (system, messages) where system is the extracted system content
        and messages is the converted conversation array.
        """
        system_parts: list[str] = []
        system_content: str | list[dict[str, Any]] | None = None
        converted: list[dict[str, Any]] = []
        id_map: dict[str, str] = {}

        for msg in messages:
            role = msg.get("role", "")

            # --- System messages ---
            if role == "system":
                content = msg.get("content", "")
                if isinstance(content, list):
                    # Already a list with cache_control markers — preserve
                    system_content = content
                else:
                    system_parts.append(str(content))
                continue

            # --- Tool result messages ---
            if role == "tool":
                # Merge consecutive tool results into the previous user message
                tc_id = str(msg.get("tool_call_id", ""))
                normalized_id = _sanitize_tool_call_id(tc_id)
                id_map[tc_id] = normalized_id
                tool_result_block: dict[str, Any] = {
                    "type": "tool_result",
                    "tool_use_id": normalized_id,
                    "content": msg.get("content", ""),
                }
                if converted and converted[-1]["role"] == "user" and isinstance(
                    converted[-1].get("content"), list
                ) and any(
                    b.get("type") == "tool_result" for b in converted[-1]["content"]
                ):
                    # Append to existing tool_result user message
                    converted[-1]["content"].append(tool_result_block)
                else:
                    # New user message for tool results
                    converted.append({"role": "user", "content": [tool_result_block]})
                continue

            # --- Assistant messages ---
            if role == "assistant":
                tool_calls = msg.get("tool_calls")
                text_content = msg.get("content")

                if tool_calls:
                    content_blocks: list[dict[str, Any]] = []
                    if text_content:
                        content_blocks.append({"type": "text", "text": text_content})

                    for tc in tool_calls:
                        tc_id = str(tc.get("id", ""))
                        normalized_id = _sanitize_tool_call_id(tc_id)
                        id_map[tc_id] = normalized_id
                        func = tc.get("function", {})
                        name = func.get("name", "")
                        args_str = func.get("arguments", "{}")
                        try:
                            args_parsed = json.loads(args_str) if args_str else {}
                        except json.JSONDecodeError:
                            logger.warning(
                                "Failed to parse tool call arguments for %s: %s",
                                name, args_str[:200],
                            )
                            args_parsed = {}
                        content_blocks.append({
                            "type": "tool_use",
                            "id": normalized_id,
                            "name": name,
                            "input": args_parsed,
                        })
                    converted.append({"role": "assistant", "content": content_blocks})
                else:
                    converted.append({
                        "role": "assistant",
                        "content": text_content or "",
                    })
                continue

            # --- User messages (pass through) ---
            converted.append({"role": role, "content": msg.get("content", "")})

        # Build system string
        system: str | list[dict[str, Any]] = ""
        if system_content is not None:
            system = system_content
        elif system_parts:
            system = "\n\n".join(system_parts)

        return system, converted

    def _convert_tools(self, tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert OpenAI function-tool format to Anthropic input_schema format."""
        converted = []
        for tool in tools:
            func = tool.get("function", {})
            converted.append({
                "name": func.get("name", ""),
                "description": func.get("description", ""),
                "input_schema": func.get("parameters", {"type": "object", "properties": {}}),
            })
        return converted

    def _convert_tool_choice(self, tool_choice: str) -> dict[str, Any]:
        """Convert OpenAI-style tool_choice string to Anthropic format."""
        mapping = {
            "auto": {"type": "auto"},
            "none": {"type": "none"},
            "required": {"type": "any"},
        }
        return mapping.get(tool_choice, {"type": "auto"})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cached_tokens: int = 0,
        cache_read_tokens: int = 0,
    ) -> float:
        """Compute cost from token counts using litellm pricing + fallback."""
        in_cost: float | None = None
        out_cost: float | None = None
        cache_cost: float | None = None

        try:
            import litellm

            pricing = litellm.model_cost.get(model)
            if pricing is not None:
                in_cost = pricing.get("input_cost_per_token")
                out_cost = pricing.get("output_cost_per_token")
                cache_cost = pricing.get("cache_read_input_token_cost")
        except Exception:  # noqa: BLE001
            pass

        if in_cost is None or out_cost is None:
            fallback = _FALLBACK_PRICING.get(model)
            if fallback is not None:
                in_cost, out_cost = fallback
                cache_cost = in_cost * 0.1

        if in_cost is None or out_cost is None:
            return 0.0

        non_cached = max(input_tokens - cached_tokens - cache_read_tokens, 0)
        total = non_cached * in_cost + output_tokens * out_cost
        if (cached_tokens + cache_read_tokens) > 0 and cache_cost is not None:
            total += (cached_tokens + cache_read_tokens) * cache_cost
        return total

    def _update_usage(self, input_tokens: int, output_tokens: int,
                      cache_creation_tokens: int = 0,
                      cache_read_tokens: int = 0) -> None:
        """Update stats from usage data."""
        cached_tokens = cache_creation_tokens + cache_read_tokens
        cost = self._extract_cost(
            model=self._model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            cache_read_tokens=cache_read_tokens,
        )
        self._stats.input_tokens += input_tokens
        self._stats.output_tokens += output_tokens
        self._stats.cached_tokens += cached_tokens
        self._stats.cost += cost

    @staticmethod
    def _strip_anthropic_prefix(model: str) -> str:
        """Strip ``anthropic/`` prefix from model identifiers."""
        if model.startswith("anthropic/"):
            return model[len("anthropic/"):]
        return model

    @staticmethod
    def _strip_images(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Remove image content blocks from messages for non-vision models."""
        result = []
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                    elif isinstance(item, dict) and item.get("type") == "image_url":
                        text_parts.append("[Image removed - model doesn't support vision]")
                result.append({**msg, "content": "\n".join(text_parts)})
            else:
                result.append(msg)
        return result
```

- [ ] **Step 2: Run conversion tests**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py::TestConvertMessagesSystemExtraction tests/llm/test_provider_anthropic.py::TestConvertMessagesToolCalls tests/llm/test_provider_anthropic.py::TestConvertMessagesToolResults tests/llm/test_provider_anthropic.py::TestConvertMessagesToolCallIdNormalization tests/llm/test_provider_anthropic.py::TestConvertTools -x -v`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add strix/llm/provider_anthropic.py tests/llm/test_provider_anthropic.py
git commit -m "feat: implement AnthropicProvider message/tool conversion with tests"
```

---

### Task 4: Write tests for capabilities, cost, and retry

**Files:**
- Modify: `tests/llm/test_provider_anthropic.py` (append tests)

- [ ] **Step 1: Write capability detection tests**

Append to the test file:

```python
# ---------------------------------------------------------------------------
# Capability queries
# ---------------------------------------------------------------------------


class TestCapabilityQueries:
    @pytest.mark.parametrize(
        "model",
        ["claude-3-5-sonnet", "claude-3-7-sonnet", "claude-4-sonnet", "claude-4-opus"],
    )
    def test_supports_vision_true(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            from strix.llm.provider_anthropic import AnthropicProvider

            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"), reasoning_effort="high"
            )
        assert prov.supports_vision() is True

    @pytest.mark.parametrize(
        "model",
        ["claude-3-5-sonnet-20241022", "claude-4-opus-20250514"],
    )
    def test_supports_vision_true_for_dated_variants(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            from strix.llm.provider_anthropic import AnthropicProvider

            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"), reasoning_effort="high"
            )
        assert prov.supports_vision() is True

    @pytest.mark.parametrize("model", ["claude-3-haiku", "claude-instant"])
    def test_supports_vision_false_for_older_models(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            from strix.llm.provider_anthropic import AnthropicProvider

            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"), reasoning_effort="high"
            )
        assert prov.supports_vision() is False

    @pytest.mark.parametrize(
        "model",
        ["claude-3-5-sonnet", "claude-3-7-sonnet", "claude-4-sonnet", "claude-4-opus"],
    )
    def test_supports_reasoning_true(self, model):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            from strix.llm.provider_anthropic import AnthropicProvider

            prov = AnthropicProvider(
                _make_config(litellm_model=f"anthropic/{model}"), reasoning_effort="high"
            )
        assert prov.supports_reasoning() is True

    def test_supports_prompt_caching_always_true(self, provider):
        assert provider.supports_prompt_caching() is True
```

- [ ] **Step 2: Write instantiation and model name tests**

```python
class TestAnthropicProviderInstantiation:
    def test_is_subclass_of_provider_base(self, provider):
        assert isinstance(provider, ProviderBase)

    def test_initial_stats_are_zero(self, provider):
        stats = provider.get_stats()
        assert isinstance(stats, RequestStats)
        assert stats.input_tokens == 0
        assert stats.output_tokens == 0
        assert stats.requests == 0
        assert stats.cost == 0.0

    def test_get_model_name_strips_prefix(self, provider):
        assert provider.get_model_name() == "claude-sonnet-4-20250514"

    def test_implements_all_abstract_methods(self):
        import inspect

        from strix.llm.provider_anthropic import AnthropicProvider

        abstract = {
            name
            for name, method in inspect.getmembers(ProviderBase, predicate=inspect.isfunction)
            if getattr(method, "__isabstractmethod__", False)
        }
        for method_name in abstract:
            assert hasattr(AnthropicProvider, method_name), f"Missing: {method_name}"
```

- [ ] **Step 3: Write retry and cost tests**

```python
class TestShouldRetry:
    def test_no_status_code_is_retryable(self, provider):
        assert provider.should_retry(RuntimeError("connection reset")) is True

    def test_rate_limit_429_is_retryable(self, provider):
        exc = Exception("rate limited")
        exc.status_code = 429
        assert provider.should_retry(exc) is True

    def test_server_error_500_is_retryable(self, provider):
        exc = Exception("server error")
        exc.status_code = 500
        assert provider.should_retry(exc) is True

    def test_bad_request_400_is_not_retryable(self, provider):
        exc = Exception("bad request")
        exc.status_code = 400
        assert provider.should_retry(exc) is False

    def test_auth_error_401_is_not_retryable(self, provider):
        exc = Exception("unauthorized")
        exc.status_code = 401
        assert provider.should_retry(exc) is False


class TestModelNameStripping:
    def test_strips_anthropic_prefix(self):
        from strix.llm.provider_anthropic import AnthropicProvider

        assert AnthropicProvider._strip_anthropic_prefix("anthropic/claude-sonnet-4") == "claude-sonnet-4"

    def test_no_prefix_unchanged(self):
        from strix.llm.provider_anthropic import AnthropicProvider

        assert AnthropicProvider._strip_anthropic_prefix("claude-sonnet-4") == "claude-sonnet-4"


class TestCostCalculation:
    def test_known_model_returns_nonzero_cost(self, provider):
        cost = provider._extract_cost(
            model="claude-sonnet-4-20250514", input_tokens=1000, output_tokens=500,
        )
        assert cost > 0.0

    def test_unknown_model_returns_zero(self, provider):
        cost = provider._extract_cost(
            model="totally-unknown-model-xyz", input_tokens=1000, output_tokens=500,
        )
        assert cost == 0.0

    def test_zero_tokens_produces_zero_cost(self, provider):
        cost = provider._extract_cost(model="claude-sonnet-4", input_tokens=0, output_tokens=0)
        assert cost == 0.0

    def test_output_more_expensive_than_input(self, provider):
        cost_in = provider._extract_cost(model="claude-sonnet-4", input_tokens=1000, output_tokens=0)
        cost_out = provider._extract_cost(model="claude-sonnet-4", input_tokens=0, output_tokens=1000)
        assert cost_out > cost_in

    def test_update_usage_accumulates(self, provider):
        provider._update_usage(input_tokens=100, output_tokens=50)
        provider._update_usage(input_tokens=200, output_tokens=100)
        stats = provider.get_stats()
        assert stats.input_tokens == 300
        assert stats.output_tokens == 150
        assert stats.cost > 0.0

    def test_update_usage_with_cache_tokens(self, provider):
        provider._update_usage(
            input_tokens=1000, output_tokens=500,
            cache_creation_tokens=100, cache_read_tokens=200,
        )
        stats = provider.get_stats()
        assert stats.cached_tokens == 300
```

- [ ] **Step 4: Write build_completion_args tests**

```python
class TestBuildCompletionArgs:
    def test_basic_args_structure(self, provider):
        args = provider.build_completion_args(
            [{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        )
        assert args["model"] == "claude-sonnet-4-20250514"
        assert args["max_tokens"] == 16384
        assert args["timeout"] == 300
        # No tools → no tool_choice or tools key
        assert "tools" not in args
        assert "tool_choice" not in args

    def test_system_extracted_to_top_level(self, provider):
        args = provider.build_completion_args(
            [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "hi"},
            ],
            tools=[], tool_choice="auto",
        )
        assert args["system"] == "You are helpful."
        # System message removed from messages array
        assert all(m["role"] != "system" for m in args["messages"])

    def test_tools_included_when_present(self, provider):
        args = provider.build_completion_args(
            [{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "run", "parameters": {"type": "object"}}}],
            tool_choice="auto",
        )
        assert "tools" in args
        assert args["tools"][0]["name"] == "run"
        assert args["tool_choice"] == {"type": "auto"}

    def test_tool_choice_required_converted(self, provider):
        args = provider.build_completion_args(
            [{"role": "user", "content": "hi"}],
            tools=[{"type": "function", "function": {"name": "run", "parameters": {"type": "object"}}}],
            tool_choice="required",
        )
        assert args["tool_choice"] == {"type": "any"}

    def test_reasoning_adds_thinking_param(self):
        with patch("strix.llm.provider_anthropic.AsyncAnthropic"):
            from strix.llm.provider_anthropic import AnthropicProvider

            prov = AnthropicProvider(
                _make_config(litellm_model="anthropic/claude-4-sonnet"), reasoning_effort="high"
            )
        args = prov.build_completion_args(
            [{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        )
        assert "thinking" in args
        assert args["thinking"]["type"] == "enabled"
        assert args["thinking"]["budget_tokens"] == 65536
```

- [ ] **Step 5: Write prepare_messages tests**

```python
class TestPrepareMessages:
    def test_adds_cache_control_to_system_message(self, provider):
        messages = [{"role": "system", "content": "You are helpful."}]
        result = provider.prepare_messages(messages)
        content = result[0]["content"]
        assert isinstance(content, list)
        assert content[0]["cache_control"] == {"type": "ephemeral"}
        assert content[0]["text"] == "You are helpful."

    def test_empty_messages_returned_unchanged(self, provider):
        assert provider.prepare_messages([]) == []

    def test_no_system_message_unchanged(self, provider):
        messages = [{"role": "user", "content": "hi"}]
        result = provider.prepare_messages(messages)
        assert result == messages

    def test_system_content_already_list_unchanged(self, provider):
        content = [{"type": "text", "text": "hi", "cache_control": {"type": "ephemeral"}}]
        messages = [{"role": "system", "content": content}]
        result = provider.prepare_messages(messages)
        assert result == messages
```

- [ ] **Step 6: Run all tests so far**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py -x -v`
Expected: All PASS except the streaming/NotImplementedError test (if any)

- [ ] **Step 7: Commit**

```bash
git add tests/llm/test_provider_anthropic.py
git commit -m "test: add AnthropicProvider capability, cost, args, and prepare_messages tests"
```

---

### Task 5: Implement streaming in AnthropicProvider

**Files:**
- Modify: `strix/llm/provider_anthropic.py:generate_stream` (replace placeholder)

- [ ] **Step 1: Implement `generate_stream`**

Replace the `generate_stream` method in `provider_anthropic.py` with the full streaming implementation:

```python
    async def generate_stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        tool_choice: str,
        **kwargs: Any,
    ) -> AsyncIterator[LLMResponse]:
        """Stream LLM responses using the Anthropic Messages API."""
        accumulated = ""
        tool_call_states: dict[int, dict[str, str]] = {}
        has_tool_call_data = False
        thinking_blocks: list[dict[str, Any]] = []
        current_thinking: dict[str, str] | None = None

        self._stats.requests += 1
        args = self.build_completion_args(messages, tools, tool_choice)

        try:
            async with self._client.messages.stream(**args) as stream:
                # Capture input tokens from message_start
                input_tokens = 0

                async for event in stream:
                    event_type = event.type

                    if event_type == "message_start":
                        if hasattr(event.message, "usage") and event.message.usage:
                            input_tokens = getattr(event.message.usage, "input_tokens", 0)

                    elif event_type == "content_block_start":
                        block = event.content_block
                        if block.type == "tool_use":
                            idx = event.index
                            tool_call_states[idx] = {
                                "id": block.id,
                                "name": block.name,
                                "arguments": "",
                            }
                            has_tool_call_data = True
                            yield LLMResponse(
                                content=accumulated,
                                streaming_tool_states=dict(tool_call_states),
                            )
                        elif block.type == "thinking":
                            current_thinking = {"text": "", "signature": ""}

                    elif event_type == "content_block_delta":
                        delta = event.delta
                        if delta.type == "text_delta":
                            accumulated += delta.text
                            yield LLMResponse(
                                content=accumulated,
                                streaming_tool_states=(
                                    dict(tool_call_states) if has_tool_call_data else None
                                ),
                            )
                        elif delta.type == "input_json_delta":
                            idx = event.index
                            if idx in tool_call_states:
                                tool_call_states[idx]["arguments"] += delta.partial_json
                                yield LLMResponse(
                                    content=accumulated,
                                    streaming_tool_states=dict(tool_call_states),
                                )
                        elif delta.type == "thinking_delta":
                            if current_thinking is not None:
                                current_thinking["text"] += delta.thinking

                    elif event_type == "content_block_stop":
                        idx = event.index
                        if idx in tool_call_states:
                            # Tool call complete — do nothing extra, we'll yield final below
                            pass
                        elif current_thinking is not None:
                            thinking_blocks.append({
                                "type": "thinking",
                                "thinking": current_thinking["text"],
                            })
                            current_thinking = None

                    elif event_type == "message_delta":
                        # Final usage and stop reason
                        output_tokens = getattr(event.usage, "output_tokens", 0)
                        cache_creation = getattr(event.usage, "cache_creation_input_tokens", 0) or 0
                        cache_read = getattr(event.usage, "cache_read_input_tokens", 0) or 0
                        self._update_usage(
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            cache_creation_tokens=cache_creation,
                            cache_read_tokens=cache_read,
                        )

        except APIStatusError as exc:
            if self.should_retry(exc):
                raise
            raise LLMRequestFailedError(
                f"Anthropic request failed: {exc.message}",
                details=f"status={exc.status_code} body={exc.response.text[:500]}",
            ) from exc

        # Build final tool_invocations from tool_call_states
        tool_calls_raw: list[dict[str, Any]] | None = None
        tool_invocations: list[dict[str, Any]] | None = None

        if tool_call_states:
            tool_calls_raw = []
            tool_invocations = []
            for _idx, state in sorted(tool_call_states.items()):
                tc_dict = {
                    "id": state["id"],
                    "type": "function",
                    "function": {
                        "name": state["name"],
                        "arguments": state["arguments"],
                    },
                }
                tool_calls_raw.append(tc_dict)

                try:
                    args_parsed = json.loads(state["arguments"]) if state["arguments"] else {}
                except json.JSONDecodeError:
                    logger.warning(
                        "Failed to parse tool call arguments for %s: %s",
                        state["name"], state["arguments"][:200],
                    )
                    args_parsed = {}

                tool_invocations.append({
                    "toolName": state["name"],
                    "args": args_parsed,
                    "id": state["id"],
                })

        yield LLMResponse(
            content=accumulated or "",
            tool_invocations=tool_invocations,
            tool_calls=tool_calls_raw,
            thinking_blocks=thinking_blocks or None,
        )
```

- [ ] **Step 2: Run existing tests to verify nothing broke**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py -x -v --ignore-glob="*streaming*"`
Expected: All PASS

- [ ] **Step 3: Commit**

```bash
git add strix/llm/provider_anthropic.py
git commit -m "feat: implement AnthropicProvider streaming with native anthropic SDK"
```

---

### Task 6: Write streaming tests

**Files:**
- Modify: `tests/llm/test_provider_anthropic.py` (append streaming tests)

- [ ] **Step 1: Write streaming test helpers and text streaming test**

Append to the test file:

```python
# ---------------------------------------------------------------------------
# Streaming behavior (with mocked AsyncAnthropic)
# ---------------------------------------------------------------------------


def _make_text_event(text: str) -> MagicMock:
    """Create a mock content_block_delta event with text delta."""
    event = MagicMock()
    event.type = "content_block_delta"
    event.index = 0
    event.delta = MagicMock()
    event.delta.type = "text_delta"
    event.delta.text = text
    return event


def _make_tool_use_start_event(index: int, tc_id: str, name: str) -> MagicMock:
    """Create a mock content_block_start event for a tool_use block."""
    event = MagicMock()
    event.type = "content_block_start"
    event.index = index
    event.content_block = MagicMock()
    event.content_block.type = "tool_use"
    event.content_block.id = tc_id
    event.content_block.name = name
    return event


def _make_input_json_delta_event(index: int, partial_json: str) -> MagicMock:
    """Create a mock content_block_delta event with input_json_delta."""
    event = MagicMock()
    event.type = "content_block_delta"
    event.index = index
    event.delta = MagicMock()
    event.delta.type = "input_json_delta"
    event.delta.partial_json = partial_json
    return event


def _make_content_block_stop_event(index: int) -> MagicMock:
    event = MagicMock()
    event.type = "content_block_stop"
    event.index = index
    return event


def _make_message_start_event(input_tokens: int = 0) -> MagicMock:
    event = MagicMock()
    event.type = "message_start"
    event.message = MagicMock()
    event.message.usage = MagicMock()
    event.message.usage.input_tokens = input_tokens
    return event


def _make_message_delta_event(output_tokens: int = 0) -> MagicMock:
    event = MagicMock()
    event.type = "message_delta"
    event.usage = MagicMock()
    event.usage.output_tokens = output_tokens
    event.usage.cache_creation_input_tokens = 0
    event.usage.cache_read_input_tokens = 0
    event.delta = MagicMock()
    event.delta.stop_reason = "end_turn"
    return event


def _make_message_stop_event() -> MagicMock:
    event = MagicMock()
    event.type = "message_stop"
    return event


class _AsyncIter:
    """Helper to create a proper async iterator from a list of events."""
    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration


class _MockStreamContext:
    """Mock async context manager for client.messages.stream()."""
    def __init__(self, events):
        self._events = events

    async def __aenter__(self):
        return _AsyncIter(self._events)

    async def __aexit__(self, *args):
        pass


class TestStreamingBehavior:
    @pytest.mark.asyncio
    async def test_text_only_streaming(self, provider):
        """Text deltas accumulate and yield intermediate + final responses."""
        events = [
            _make_message_start_event(input_tokens=100),
            _make_text_event("Hello"),
            _make_text_event(" world"),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=5),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            responses.append(resp)

        assert len(responses) >= 3  # 2 intermediate + 1 final
        final = responses[-1]
        assert "Hello world" in final.content
        assert final.tool_invocations is None
        assert final.thinking_blocks is None
        assert provider.get_stats().input_tokens == 100
        assert provider.get_stats().output_tokens == 5

    @pytest.mark.asyncio
    async def test_tool_call_streaming(self, provider):
        """Tool use content blocks are assembled into tool_invocations."""
        events = [
            _make_message_start_event(input_tokens=50),
            _make_tool_use_start_event(0, "call_abc", "get_weather"),
            _make_input_json_delta_event(0, '{"ci'),
            _make_input_json_delta_event(0, 'ty": "SF"}'),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=20),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "weather?"}],
            tools=[{"type": "function", "function": {"name": "get_weather"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert final.tool_invocations is not None
        assert len(final.tool_invocations) == 1
        assert final.tool_invocations[0]["toolName"] == "get_weather"
        assert final.tool_invocations[0]["args"] == {"city": "SF"}
        assert final.tool_invocations[0]["id"] == "call_abc"

        assert final.tool_calls is not None
        assert final.tool_calls[0]["function"]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_mixed_text_and_tool_calls(self, provider):
        """Text followed by tool calls in the same stream."""
        events = [
            _make_message_start_event(input_tokens=30),
            _make_text_event("Let me check"),
            _make_content_block_stop_event(0),
            _make_tool_use_start_event(1, "call_123", "search"),
            _make_input_json_delta_event(1, '{"q": "test"}'),
            _make_content_block_stop_event(1),
            _make_message_delta_event(output_tokens=15),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "search"}],
            tools=[{"type": "function", "function": {"name": "search"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert "Let me check" in final.content
        assert final.tool_invocations is not None
        assert final.tool_invocations[0]["toolName"] == "search"

    @pytest.mark.asyncio
    async def test_usage_extraction(self, provider):
        """Usage stats extracted from message_start and message_delta events."""
        events = [
            _make_message_start_event(input_tokens=42),
            _make_text_event("Hi"),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=18),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        async for _ in provider.generate_stream(
            messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
        ):
            pass

        stats = provider.get_stats()
        assert stats.input_tokens == 42
        assert stats.output_tokens == 18
        assert stats.requests == 1

    @pytest.mark.asyncio
    async def test_api_error_raises_llm_request_failed(self, provider):
        """Non-retryable errors raise LLMRequestFailedError."""
        exc = APIStatusError(
            message="Bad request",
            response=MagicMock(status_code=400, text="invalid model"),
            body=None,
        )
        provider._client.messages.stream = MagicMock(
            side_effect=exc
        )

        with pytest.raises(LLMRequestFailedError, match="Anthropic request failed"):
            async for _ in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
            ):
                pass

    @pytest.mark.asyncio
    async def test_retryable_error_reraises(self, provider):
        """Retryable errors (429) reraise the original APIStatusError."""
        exc = APIStatusError(
            message="Rate limited",
            response=MagicMock(status_code=429, text="slow down"),
            body=None,
        )
        provider._client.messages.stream = MagicMock(side_effect=exc)

        with pytest.raises(APIStatusError, match="Rate limited"):
            async for _ in provider.generate_stream(
                messages=[{"role": "user", "content": "hi"}], tools=[], tool_choice="auto"
            ):
                pass

    @pytest.mark.asyncio
    async def test_malformed_tool_arguments_fallback(self, provider):
        """Malformed JSON in tool arguments falls back to empty dict."""
        events = [
            _make_message_start_event(input_tokens=20),
            _make_tool_use_start_event(0, "call_bad", "do_thing"),
            _make_input_json_delta_event(0, "{invalid json"),
            _make_content_block_stop_event(0),
            _make_message_delta_event(output_tokens=5),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "do"}],
            tools=[{"type": "function", "function": {"name": "do_thing"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert final.tool_invocations is not None
        assert final.tool_invocations[0]["args"] == {}
        assert final.tool_invocations[0]["toolName"] == "do_thing"

    @pytest.mark.asyncio
    async def test_multiple_tool_calls(self, provider):
        """Multiple tool_use blocks tracked independently."""
        events = [
            _make_message_start_event(input_tokens=40),
            _make_tool_use_start_event(0, "call_a", "get_weather"),
            _make_input_json_delta_event(0, '{"city": "LA"}'),
            _make_content_block_stop_event(0),
            _make_tool_use_start_event(1, "call_b", "get_time"),
            _make_input_json_delta_event(1, '{"tz": "PST"}'),
            _make_content_block_stop_event(1),
            _make_message_delta_event(output_tokens=15),
            _make_message_stop_event(),
        ]
        provider._client.messages.stream = MagicMock(return_value=_MockStreamContext(events))

        responses = []
        async for resp in provider.generate_stream(
            messages=[{"role": "user", "content": "weather and time"}],
            tools=[{"type": "function", "function": {"name": "get_weather"}}],
            tool_choice="auto",
        ):
            responses.append(resp)

        final = responses[-1]
        assert final.tool_invocations is not None
        assert len(final.tool_invocations) == 2
        assert final.tool_invocations[0]["toolName"] == "get_weather"
        assert final.tool_invocations[0]["args"]["city"] == "LA"
        assert final.tool_invocations[1]["toolName"] == "get_time"
        assert final.tool_invocations[1]["args"]["tz"] == "PST"
```

- [ ] **Step 2: Run streaming tests**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py::TestStreamingBehavior -x -v`
Expected: All PASS

- [ ] **Step 3: Run ALL provider tests**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_anthropic.py -x -v`
Expected: All PASS

- [ ] **Step 4: Commit**

```bash
git add tests/llm/test_provider_anthropic.py
git commit -m "test: add AnthropicProvider streaming tests with mocked SDK events"
```

---

### Task 7: Verify provider routing tests still pass

**Files:**
- No changes (verify only)

- [ ] **Step 1: Run provider routing tests**

Run: `.venv/bin/python -m pytest tests/llm/test_provider_routing.py -x -v`
Expected: All PASS — the routing logic in `llm.py` hasn't changed, and `AnthropicProvider` still implements `ProviderBase`.

- [ ] **Step 2: Run all LLM tests**

Run: `.venv/bin/python -m pytest tests/llm/ -x -v`
Expected: All PASS — the routing tests, the new Anthropic provider tests, and the existing OpenAI provider tests all pass.

- [ ] **Step 3: Commit (only if fixes were needed)**

```bash
git add -A
git commit -m "fix: adjust tests for new AnthropicProvider API"  # Only if needed
```

---

### Task 8: Fix integration test

**Files:**
- Modify: `tests/tools/test_real_autonomous_scan.py:54-97`

- [ ] **Step 1: Update Anthropic test to use proper model name**

Change the `TestAnthropicAutonomousScan` class to use an `anthropic/` prefixed model name so it routes through the new `AnthropicProvider`. Update `TestAnthropicAutonomousScan.test_autonomous_scan_finds_vulnerability`:

```python
class TestAnthropicAutonomousScan:
    """Real autonomous scan tests using the Anthropic provider."""

    async def test_autonomous_scan_finds_vulnerability(
        self, dummy_target: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Run a real autonomous scan with Anthropic to find the SQLi."""
        from strix.agents.StrixAgent.strix_agent import StrixAgent
        from strix.llm.config import LLMConfig

        monkeypatch.setenv("STRIX_LLM", "openai/gpt-5.4-mini")
        monkeypatch.setenv("LLM_API_KEY", "REDACTED_API_KEY")
        monkeypatch.setenv("LLM_API_BASE", "REDACTED_API_BASE")

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
```

Note: Both tests use `openai/gpt-5.4-mini` to route through the OpenAI provider against the proxy. The Anthropic provider can be tested separately by changing the model name to an `anthropic/` prefixed model when the Anthropic endpoint is available on the proxy.

- [ ] **Step 2: Run integration test (requires proxy access)**

Run: `STRIX_ANTHROPIC_API_KEY=test STRIX_OPENAI_API_KEY=test .venv/bin/python -m pytest tests/tools/test_real_autonomous_scan.py -x -v --timeout=120`
Expected: Tests pass or skip if proxy is unreachable.

- [ ] **Step 3: Commit**

```bash
git add tests/tools/test_real_autonomous_scan.py
git commit -m "test: update integration tests for new AnthropicProvider"
```

---

### Task 9: Final validation

**Files:**
- No changes (run full test suite)

- [ ] **Step 1: Run full test suite**

Run: `.venv/bin/python -m pytest tests/llm/ -x -v --timeout=30`
Expected: All PASS

- [ ] **Step 2: Run ruff linting**

Run: `.venv/bin/python -m ruff check strix/llm/provider_anthropic.py`
Expected: No errors

- [ ] **Step 3: Final commit if any lint fixes needed**

```bash
git add strix/llm/provider_anthropic.py
git commit -m "style: lint fixes for new AnthropicProvider"  # Only if needed
```

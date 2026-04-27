# AnthropicProvider Migration: litellm → Native anthropic SDK

## Problem

`AnthropicProvider` delegates all Anthropic API interaction to litellm, which acts as
an opinionated middleware layer. This causes two concrete issues:

1. **Proxy incompatibility** — litellm auto-extracts system messages into Anthropic's
   top-level `system` parameter. When routing through an OpenAI-compatible proxy that
   doesn't expect this parameter, requests fail with `AnthropicException: unexpected
   keyword argument 'system'`. The same proxy works fine in Claude Code and other
   clients that use the native Anthropic SDK directly.

2. **Unnecessary abstraction** — litellm adds a heavy dependency for what amounts to
   format conversion between OpenAI-style and Anthropic-style APIs. The OpenAI provider
   already bypasses litellm for actual API calls (using only its pricing database), and
   the Anthropic provider should do the same.

## Approach

Rewrite `AnthropicProvider` to use the official `anthropic` Python SDK (`AsyncAnthropic`),
matching the pattern already established by `OpenAIProvider` which uses the native
`openai` SDK. No changes to `ProviderBase`, `OpenAIProvider`, or provider routing.

### Scope

| File | Action |
|------|--------|
| `strix/llm/provider_anthropic.py` | Full rewrite |
| `pyproject.toml` | Add `anthropic` dependency |
| `tests/tools/test_real_autonomous_scan.py` | Fix Anthropic test routing |

**Out of scope**: litellm usage in `dedupe.py`, `memory_compressor.py`, `main.py`.

## Architecture

```
ProviderBase (ABC, unchanged)
├── OpenAIProvider (unchanged)
│   └── AsyncOpenAI client
└── AnthropicProvider (rewrite)
    └── AsyncAnthropic client
```

Provider routing in `llm.py` stays the same — models starting with `openai/` route to
OpenAI provider, everything else to Anthropic provider.

## Detailed Design

### 1. Client Construction

```python
from anthropic import AsyncAnthropic

class AnthropicProvider(ProviderBase):
    def __init__(self, config: LLMConfig, reasoning_effort: str) -> None:
        self._config = config
        self._reasoning_effort = reasoning_effort
        self._stats = RequestStats()
        self._model_name = self._strip_anthropic_prefix(config.litellm_model)
        self._client = AsyncAnthropic(
            api_key=config.api_key or None,
            base_url=config.api_base or None,
        )
```

The model name strips any `anthropic/` prefix so the SDK gets a clean model identifier
like `claude-sonnet-4-20250514` instead of `anthropic/claude-sonnet-4-20250514`.

### 2. Message Format Conversion

Internal messages are OpenAI-style dicts. Anthropic Messages API has three key
differences:

1. **System messages** are a top-level `system` parameter, not in the messages array
2. **Tool calls** are `tool_use` content blocks on assistant messages, not a separate
   `tool_calls` field
3. **Tool results** are `tool_result` content blocks on user messages, not separate
   `tool` role messages

A `_convert_messages()` method handles this transformation:

```python
def _convert_messages(
    self, messages: list[dict[str, Any]]
) -> tuple[str | list[dict], list[dict[str, Any]]]:
    """Convert OpenAI-style messages to Anthropic format.

    Returns (system, messages) where system is the extracted system content
    and messages is the converted conversation array.
    """
```

**System extraction**: Collect all `system` role messages into a single system string
(or list of content blocks if prompt caching markers are present).

**Assistant messages with tool_calls**: Convert each tool call to a `tool_use` content
block:
```python
# OpenAI format:
{"role": "assistant", "content": "...", "tool_calls": [
    {"id": "call_123", "function": {"name": "read_file", "arguments": "{...}"}}
]}
# Anthropic format:
{"role": "assistant", "content": [
    {"type": "text", "text": "..."},
    {"type": "tool_use", "id": "call_123", "name": "read_file", "input": {...}}
]}
```

Note: `arguments` is a JSON string in OpenAI but `input` is a parsed dict in Anthropic.

**Tool result messages**: Convert `tool` role messages to `user` role with `tool_result`
content blocks. Consecutive tool results are merged into a single user message:
```python
# OpenAI format:
{"role": "tool", "tool_call_id": "call_123", "content": "file contents..."}
# Anthropic format:
{"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": "call_123", "content": "file contents..."}
]}
```

**Tool call ID normalization**: Anthropic requires IDs matching `^[a-zA-Z0-9_-]+$`
(max 64 chars). If an ID doesn't match, sanitize it by stripping invalid characters
and truncating.

### 3. Tool Definition Conversion

OpenAI and Anthropic use different schemas for tool definitions:

```python
def _convert_tools(
    self, tools: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Convert OpenAI function-tool format to Anthropic input_schema format."""
```

```python
# OpenAI format:
{"type": "function", "function": {
    "name": "read_file",
    "description": "Read a file",
    "parameters": {"type": "object", "properties": {...}, "required": [...]}
}}
# Anthropic format:
{"name": "read_file",
 "description": "Read a file",
 "input_schema": {"type": "object", "properties": {...}, "required": [...]}
}}
```

### 4. Streaming

Use `client.messages.stream()` — the SDK's native streaming context manager:

```python
async with self._client.messages.stream(**params) as stream:
    async for event in stream:
        # Process events
```

Event types to handle:

| Event | Action |
|-------|--------|
| `text` delta | Accumulate content, yield intermediate `LLMResponse` |
| `tool_use` content_block start | Initialize tool call state |
| `input_json` delta | Accumulate partial JSON arguments |
| `content_block_stop` | Finalize tool call, parse arguments |
| `message_stop` | Extract usage stats, yield final `LLMResponse` |

The streaming pattern mirrors `OpenAIProvider.generate_stream()`:
- Accumulate text content across chunks
- Track partial tool calls in `tool_call_states` dict
- Yield intermediate `LLMResponse` with `streaming_tool_states` for TUI rendering
- Yield final `LLMResponse` with complete `tool_invocations` and `tool_calls`

### 5. Prompt Caching

Anthropic supports prompt caching via `cache_control` markers on content blocks.
Applied in `prepare_messages()`:

- System message content gets `cache_control: {"type": "ephemeral"}`
- Last user message's last content block gets the same marker

Only applied when `supports_prompt_caching()` returns True.

### 6. Capability Detection

Replace litellm's `supports_*` functions with model-name heuristics:

```python
_REASONING_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet", "claude-3-7-sonnet",
    "claude-4-sonnet", "claude-4-opus",
})
_VISION_MODELS: frozenset[str] = frozenset({
    "claude-3-5-sonnet", "claude-3-7-sonnet",
    "claude-4-sonnet", "claude-4-opus",
})

def supports_vision(self) -> bool:
    base = self._model_name
    return any(base == m or base.startswith(m + "-") for m in _VISION_MODELS)

def supports_reasoning(self) -> bool:
    base = self._model_name
    return any(base == m or base.startswith(m + "-") for m in _REASONING_MODELS)

def supports_prompt_caching(self) -> bool:
    return True  # All modern Anthropic models support prompt caching
```

### 7. Cost Calculation

Same approach as `OpenAIProvider`:

1. Try `litellm.model_cost` pricing database (shallow dependency — just dict lookup)
2. Fall back to static `_FALLBACK_PRICING` table for Claude models not yet in litellm
3. Compute cost from token counts: `input * rate + output * rate + cached * cache_rate`

```python
_FALLBACK_PRICING: dict[str, tuple[float, float]] = {
    "claude-sonnet-4": (3e-6, 1.5e-5),
    "claude-opus-4": (1.5e-5, 7.5e-5),
    "claude-3-5-sonnet": (3e-6, 1.5e-5),
    # ... etc
}
```

### 8. Error Handling and Retry

```python
from anthropic import APIStatusError

_RETRYABLE_STATUS_CODES: frozenset[int] = frozenset({429, 500, 502, 503})

def should_retry(self, exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code is None:
        return True  # Connection errors, timeouts
    return status_code in _RETRYABLE_STATUS_CODES
```

In `generate_stream()`, non-retryable errors raise `LLMRequestFailedError` (same
pattern as OpenAI provider). Malformed tool call JSON falls back to empty args with
a warning log.

### 9. Reasoning (Extended Thinking)

For models that support reasoning, include `thinking` parameter:

```python
if self.supports_reasoning():
    params["thinking"] = {
        "type": "enabled",
        "budget_tokens": self._get_thinking_budget(),
    }
```

Budget maps from reasoning_effort: `"low"` → 4096, `"medium"` → 16384, `"high"` → 65536.
Thinking blocks are extracted from the response and passed through in
`LLMResponse.thinking_blocks`.

### 10. Method Summary

| Method | Change |
|--------|--------|
| `__init__` | Create `AsyncAnthropic` client |
| `generate_stream` | Full rewrite using `client.messages.stream()` |
| `build_completion_args` | Rewrite: extract system, call converters |
| `prepare_messages` | Rewrite: add `cache_control` markers |
| `should_retry` | Simplify: check `APIStatusError.status_code` |
| `supports_vision` | Model-name heuristic |
| `supports_reasoning` | Model-name heuristic |
| `supports_prompt_caching` | Always True |
| `_convert_messages` | **New**: OpenAI → Anthropic message format |
| `_convert_tools` | **New**: OpenAI → Anthropic tool format |
| `_strip_anthropic_prefix` | **New**: strip `anthropic/` from model name |
| `_get_thinking_budget` | **New**: effort → token budget mapping |

## Testing

1. **Fix `test_real_autonomous_scan.py`**: Change Anthropic test to use
   `anthropic/claude-sonnet-4-20250514` model name to route through the new provider.
2. **Unit tests**: Add tests for `_convert_messages` and `_convert_tools` with various
   message patterns (system-only, with tool calls, with tool results, mixed).
3. **Integration test**: The existing live autonomous scan test validates the full
   pipeline end-to-end.

## Dependencies

- Add `anthropic` to `pyproject.toml` dependencies
- Retain `litellm` dependency (used by dedupe, memory_compressor, main; also used
  shallowly for pricing lookups in both providers)

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import litellm
from jinja2 import Environment, FileSystemLoader, select_autoescape
from litellm import acompletion, completion_cost, stream_chunk_builder, supports_reasoning
from litellm.utils import supports_prompt_caching, supports_vision

from strix.config import Config
from strix.llm.config import LLMConfig
from strix.llm.memory_compressor import MemoryCompressor
from strix.skills import load_skills
from strix.tools.registry import get_tools_definitions
from strix.utils.resource_paths import get_strix_resource_path

logger = logging.getLogger(__name__)


litellm.drop_params = True
litellm.modify_params = True


class LLMRequestFailedError(Exception):
    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


@dataclass
class LLMResponse:
    content: str
    tool_invocations: list[dict[str, Any]] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    thinking_blocks: list[dict[str, Any]] | None = None
    # Partial tool-call state during streaming.  Maps tool-call index →
    # ``{"id": str, "name": str, "arguments": str}`` where *arguments* is
    # the raw accumulated JSON fragment.  ``None`` when no tool-call data
    # has been seen yet on this response.
    streaming_tool_states: dict[int, dict[str, str]] | None = None


@dataclass
class RequestStats:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost: float = 0.0
    requests: int = 0

    def to_dict(self) -> dict[str, int | float]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "cost": round(self.cost, 4),
            "requests": self.requests,
        }


class LLM:
    def __init__(self, config: LLMConfig, agent_name: str | None = None):
        self.config = config
        self.agent_name = agent_name
        self.agent_id: str | None = None
        self._active_skills: list[str] = list(config.skills or [])
        self._system_prompt_context: dict[str, Any] = dict(
            getattr(config, "system_prompt_context", {}) or {}
        )
        self._total_stats = RequestStats()
        self.memory_compressor = MemoryCompressor(model_name=config.litellm_model)
        self.system_prompt = self._load_system_prompt(agent_name)

        reasoning = Config.get("strix_reasoning_effort")
        if reasoning:
            self._reasoning_effort = reasoning
        elif config.reasoning_effort:
            self._reasoning_effort = config.reasoning_effort
        elif config.scan_mode == "quick":
            self._reasoning_effort = "medium"
        else:
            self._reasoning_effort = "high"

    def _load_system_prompt(self, agent_name: str | None) -> str:
        if not agent_name:
            return ""

        try:
            prompt_dir = get_strix_resource_path("agents", agent_name)
            skills_dir = get_strix_resource_path("skills")
            env = Environment(
                loader=FileSystemLoader([prompt_dir, skills_dir]),
                autoescape=select_autoescape(enabled_extensions=(), default_for_string=False),
            )

            skills_to_load = self._get_skills_to_load()
            skill_content = load_skills(skills_to_load)
            env.globals["get_skill"] = lambda name: skill_content.get(name, "")

            result = env.get_template("system_prompt.jinja").render(
                loaded_skill_names=list(skill_content.keys()),
                interactive=self.config.interactive,
                system_prompt_context=self._system_prompt_context,
                **skill_content,
            )
            return str(result)
        except Exception:  # noqa: BLE001
            return ""

    def _get_skills_to_load(self) -> list[str]:
        ordered_skills = [*self._active_skills]
        ordered_skills.append(f"scan_modes/{self.config.scan_mode}")
        if self.config.is_whitebox:
            ordered_skills.append("coordination/source_aware_whitebox")
            ordered_skills.append("custom/source_aware_sast")

        deduped: list[str] = []
        seen: set[str] = set()
        for skill_name in ordered_skills:
            if skill_name not in seen:
                deduped.append(skill_name)
                seen.add(skill_name)

        return deduped

    def add_skills(self, skill_names: list[str]) -> list[str]:
        added: list[str] = []
        for skill_name in skill_names:
            if not skill_name or skill_name in self._active_skills:
                continue
            self._active_skills.append(skill_name)
            added.append(skill_name)

        if not added:
            return []

        updated_prompt = self._load_system_prompt(self.agent_name)
        if updated_prompt:
            self.system_prompt = updated_prompt

        return added

    def set_agent_identity(self, agent_name: str | None, agent_id: str | None) -> None:
        if agent_name:
            self.agent_name = agent_name
        if agent_id:
            self.agent_id = agent_id

    def set_system_prompt_context(self, context: dict[str, Any] | None) -> None:
        self._system_prompt_context = dict(context or {})
        updated_prompt = self._load_system_prompt(self.agent_name)
        if updated_prompt:
            self.system_prompt = updated_prompt

    async def generate(
        self, conversation_history: list[dict[str, Any]]
    ) -> AsyncIterator[LLMResponse]:
        messages = self._prepare_messages(conversation_history)
        max_retries = int(Config.get("strix_llm_max_retries") or "5")

        for attempt in range(max_retries + 1):
            try:
                async for response in self._stream(messages):
                    yield response
                return  # noqa: TRY300
            except Exception as e:  # noqa: BLE001
                if attempt >= max_retries or not self._should_retry(e):
                    self._raise_error(e)
                wait = min(90, 2 * (2**attempt))
                await asyncio.sleep(wait)

    async def _stream(self, messages: list[dict[str, Any]]) -> AsyncIterator[LLMResponse]:
        accumulated = ""
        chunks: list[Any] = []
        done_streaming = 0

        # Track partial tool-call state during streaming so the TUI can
        # render tool calls forming in real-time.
        tool_call_states: dict[int, dict[str, str]] = {}
        has_tool_call_data = False

        self._total_stats.requests += 1
        response = await acompletion(**self._build_completion_args(messages), stream=True)

        async for chunk in response:
            chunks.append(chunk)
            if done_streaming:
                done_streaming += 1
                if getattr(chunk, "usage", None) or done_streaming > 5:
                    break
                continue

            # Extract text delta
            text_delta = self._get_chunk_content(chunk)
            if text_delta:
                accumulated += text_delta

            # Extract tool-call deltas from this chunk
            raw_delta = None
            if chunk.choices and hasattr(chunk.choices[0], "delta"):
                raw_delta = chunk.choices[0].delta

            tc_deltas = getattr(raw_delta, "tool_calls", None) if raw_delta else None
            if tc_deltas:
                has_tool_call_data = True
                for tc in tc_deltas:
                    idx = getattr(tc, "index", 0)
                    if idx not in tool_call_states:
                        tool_call_states[idx] = {"id": "", "name": "", "arguments": ""}
                    state = tool_call_states[idx]
                    tc_id = getattr(tc, "id", None)
                    if tc_id:
                        state["id"] = tc_id
                    func = getattr(tc, "function", None)
                    if func is not None:
                        name = getattr(func, "name", None)
                        if name:
                            state["name"] = name
                        arguments = getattr(func, "arguments", None)
                        if arguments:
                            state["arguments"] += arguments

            # Yield intermediate response if there's new content or tool data
            if text_delta or tc_deltas:
                yield LLMResponse(
                    content=accumulated,
                    streaming_tool_states=dict(tool_call_states) if has_tool_call_data else None,
                )

        # Build the complete response from chunks for metadata extraction
        built_response = None
        if chunks:
            try:
                built_response = stream_chunk_builder(chunks)
                self._update_usage_stats(built_response)
            except Exception:  # noqa: BLE001
                logger.warning("Failed to build stream response for usage stats")

        # Extract native tool_calls from the response
        tool_calls_raw: list[dict[str, Any]] | None = None
        tool_invocations: list[dict[str, Any]] | None = None

        if built_response and built_response.choices:
            message = built_response.choices[0].message
            raw_tool_calls = getattr(message, "tool_calls", None)

            if raw_tool_calls:
                tool_calls_raw = []
                tool_invocations = []
                for tc in raw_tool_calls:
                    tc_dict = {
                        "id": tc.id,
                        "type": getattr(tc, "type", "function"),
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    tool_calls_raw.append(tc_dict)

                    # Parse arguments JSON string to typed args dict
                    try:
                        args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                    except json.JSONDecodeError:
                        logger.warning(
                            "Failed to parse tool call arguments for %s: %s",
                            tc.function.name,
                            tc.function.arguments[:200],
                        )
                        args = {}

                    tool_invocations.append({
                        "toolName": tc.function.name,
                        "args": args,
                        "id": tc.id,
                    })

        # Use content from accumulated streaming text, or from the built response
        final_content = accumulated
        if not final_content and built_response and built_response.choices:
            msg_content = getattr(built_response.choices[0].message, "content", None)
            if msg_content:
                final_content = msg_content

        yield LLMResponse(
            content=final_content or "",
            tool_invocations=tool_invocations,
            tool_calls=tool_calls_raw,
            thinking_blocks=self._extract_thinking(chunks),
        )

    def _prepare_messages(self, conversation_history: list[dict[str, Any]]) -> list[dict[str, Any]]:
        messages = [{"role": "system", "content": self.system_prompt}]

        if self.agent_name:
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"\n\n<agent_identity>\n"
                        f"<meta>Internal metadata: do not echo or reference.</meta>\n"
                        f"<agent_name>{self.agent_name}</agent_name>\n"
                        f"<agent_id>{self.agent_id}</agent_id>\n"
                        f"</agent_identity>\n\n"
                    ),
                }
            )

        compressed = list(self.memory_compressor.compress_history(conversation_history))
        conversation_history.clear()
        conversation_history.extend(compressed)

        # Convert conversation history to LiteLLM-compatible format.
        # Handles two formats:
        # 1. Native: assistant+tool_calls followed by tool role messages (from native executor)
        # 2. Legacy: assistant+tool_calls followed by user "Tool Results:" with XML (old executor)
        i = 0
        while i < len(compressed):
            msg = compressed[i]

            # Tool role messages — pass through with tool_call_id intact
            if msg.get("role") == "tool":
                api_msg: dict[str, Any] = {
                    "role": "tool",
                    "tool_call_id": msg.get("tool_call_id", ""),
                    "content": msg.get("content", ""),
                }
                messages.append(api_msg)
                i += 1
                continue

            # Assistant message with native tool_calls → include tool_calls for API
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                api_msg = {
                    "role": "assistant",
                    "content": msg.get("content") or None,
                    "tool_calls": msg["tool_calls"],
                }
                messages.append(api_msg)

                # Check if next message is legacy XML-format tool results (user message)
                if i + 1 < len(compressed):
                    next_msg = compressed[i + 1]
                    if (
                        next_msg.get("role") == "user"
                        and isinstance(next_msg.get("content"), str)
                        and "Tool Results:" in next_msg.get("content", "")
                    ):
                        tool_messages = self._convert_tool_results_to_tool_messages(
                            next_msg["content"], msg["tool_calls"]
                        )
                        messages.extend(tool_messages)
                        i += 2  # Skip both the assistant and the user (tool results) message
                        continue
                    elif (
                        next_msg.get("role") == "user"
                        and isinstance(next_msg.get("content"), list)
                    ):
                        # Handle legacy image-containing tool results
                        text_content = ""
                        for part in next_msg["content"]:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_content = part.get("text", "")
                                break
                        if "Tool Results:" in text_content:
                            tool_messages = self._convert_tool_results_to_tool_messages(
                                text_content, msg["tool_calls"]
                            )
                            messages.extend(tool_messages)
                            i += 2
                            continue

                i += 1
                continue

            # Regular message — pass through as-is (strip internal keys)
            api_msg = {"role": msg["role"], "content": msg.get("content", "")}
            messages.append(api_msg)
            i += 1

        if messages[-1].get("role") == "assistant" and not self.config.interactive:
            messages.append({"role": "user", "content": "<meta>Continue the task.</meta>"})

        if self._is_anthropic() and self.config.enable_prompt_caching:
            messages = self._add_cache_control(messages)

        return messages

    @staticmethod
    def _convert_tool_results_to_tool_messages(
        results_content: str, tool_calls: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Convert a combined tool-results user message into individual tool role messages.

        The executor stores all tool results in a single user message like:
            "Tool Results:\\n\\n<tool_result>\\n<tool_name>X</tool_name>\\n<result>...</result>\\n</tool_result>"

        We split by <tool_result> blocks and match them to tool_calls by name or position.
        """
        import re

        # Extract individual tool result blocks
        result_blocks: list[tuple[str, str]] = []  # (tool_name, result_text)
        pattern = re.compile(
            r"<tool_result>\s*<tool_name>(.*?)</tool_name>\s*<result>(.*?)</result>\s*</tool_result>",
            re.DOTALL,
        )
        for m in pattern.finditer(results_content):
            result_blocks.append((m.group(1).strip(), m.group(2)))

        # If no XML blocks found, use the full content as a single result
        if not result_blocks:
            result_blocks = [("", results_content)]

        # Build tool role messages, matching by name then falling back to position
        tool_messages: list[dict[str, Any]] = []
        used_indices: set[int] = set()

        for block_name, block_result in result_blocks:
            matched_id = None

            # Try to match by function name
            if block_name:
                for idx, tc in enumerate(tool_calls):
                    if idx not in used_indices and tc.get("function", {}).get("name") == block_name:
                        matched_id = tc["id"]
                        used_indices.add(idx)
                        break

            # Fall back to positional matching
            if matched_id is None:
                for idx, tc in enumerate(tool_calls):
                    if idx not in used_indices:
                        matched_id = tc["id"]
                        used_indices.add(idx)
                        break

            # Last resort: use first tool_call id
            if matched_id is None and tool_calls:
                matched_id = tool_calls[0]["id"]

            if matched_id:
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": matched_id,
                    "content": block_result,
                })

        return tool_messages

    def _build_completion_args(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._supports_vision():
            messages = self._strip_images(messages)

        args: dict[str, Any] = {
            "model": self.config.litellm_model,
            "messages": messages,
            "timeout": self.config.timeout,
            "stream_options": {"include_usage": True},
            "tools": get_tools_definitions(),
            "tool_choice": "auto",
        }

        if self.config.api_key:
            args["api_key"] = self.config.api_key
        if self.config.api_base:
            args["api_base"] = self.config.api_base
        if self._supports_reasoning():
            args["reasoning_effort"] = self._reasoning_effort

        return args

    def _get_chunk_content(self, chunk: Any) -> str:
        if chunk.choices and hasattr(chunk.choices[0], "delta"):
            return getattr(chunk.choices[0].delta, "content", "") or ""
        return ""

    def _extract_thinking(self, chunks: list[Any]) -> list[dict[str, Any]] | None:
        if not chunks or not self._supports_reasoning():
            return None
        try:
            resp = stream_chunk_builder(chunks)
            if resp.choices and hasattr(resp.choices[0].message, "thinking_blocks"):
                blocks: list[dict[str, Any]] = resp.choices[0].message.thinking_blocks
                return blocks
        except Exception:  # noqa: BLE001, S110  # nosec B110
            pass
        return None

    def _update_usage_stats(self, response: Any) -> None:
        try:
            if hasattr(response, "usage") and response.usage:
                input_tokens = getattr(response.usage, "prompt_tokens", 0) or 0
                output_tokens = getattr(response.usage, "completion_tokens", 0) or 0

                cached_tokens = 0
                if hasattr(response.usage, "prompt_tokens_details"):
                    prompt_details = response.usage.prompt_tokens_details
                    if hasattr(prompt_details, "cached_tokens"):
                        cached_tokens = prompt_details.cached_tokens or 0

                cost = self._extract_cost(response)
            else:
                input_tokens = 0
                output_tokens = 0
                cached_tokens = 0
                cost = 0.0

            self._total_stats.input_tokens += input_tokens
            self._total_stats.output_tokens += output_tokens
            self._total_stats.cached_tokens += cached_tokens
            self._total_stats.cost += cost

        except Exception:  # noqa: BLE001, S110  # nosec B110
            pass

    def _extract_cost(self, response: Any) -> float:
        if hasattr(response, "usage") and response.usage:
            direct_cost = getattr(response.usage, "cost", None)
            if direct_cost is not None:
                return float(direct_cost)
        try:
            if hasattr(response, "_hidden_params"):
                response._hidden_params.pop("custom_llm_provider", None)
            return completion_cost(response, model=self.config.canonical_model) or 0.0
        except Exception:  # noqa: BLE001
            return 0.0

    def _should_retry(self, e: Exception) -> bool:
        code = getattr(e, "status_code", None) or getattr(
            getattr(e, "response", None), "status_code", None
        )
        return code is None or litellm._should_retry(code)

    def _raise_error(self, e: Exception) -> None:
        from strix.telemetry import posthog

        posthog.error("llm_error", type(e).__name__)
        raise LLMRequestFailedError(f"LLM request failed: {type(e).__name__}", str(e)) from e

    def _is_anthropic(self) -> bool:
        if not self.config.model_name:
            return False
        return any(p in self.config.model_name.lower() for p in ["anthropic/", "claude"])

    def _supports_vision(self) -> bool:
        try:
            return bool(supports_vision(model=self.config.canonical_model))
        except Exception:  # noqa: BLE001
            return False

    def _supports_reasoning(self) -> bool:
        try:
            return bool(supports_reasoning(model=self.config.canonical_model))
        except Exception:  # noqa: BLE001
            return False

    def _strip_images(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
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

    def _add_cache_control(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not messages or not supports_prompt_caching(self.config.canonical_model):
            return messages

        result = list(messages)

        if result[0].get("role") == "system":
            content = result[0]["content"]
            result[0] = {
                **result[0],
                "content": [
                    {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
                ]
                if isinstance(content, str)
                else content,
            }
        return result

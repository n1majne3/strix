import asyncio
import logging
from collections.abc import AsyncIterator
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from strix.config import Config
from strix.llm.config import LLMConfig
from strix.llm.memory_compressor import MemoryCompressor
from strix.llm.provider_base import LLMRequestFailedError, LLMResponse, RequestStats
from strix.skills import load_skills
from strix.utils.resource_paths import get_strix_resource_path

logger = logging.getLogger(__name__)


def get_provider(config: LLMConfig, reasoning_effort: str) -> "ProviderBase":
    """Return the appropriate provider based on canonical model name."""
    from strix.llm.provider_anthropic import AnthropicProvider
    from strix.llm.provider_openai import OpenAIProvider

    from strix.llm.provider_base import ProviderBase

    canonical = config.canonical_model or ""
    if canonical.startswith("openai/"):
        return OpenAIProvider(config, reasoning_effort)
    # Default to Anthropic (covers anthropic/ and any unrecognized prefix)
    return AnthropicProvider(config, reasoning_effort)


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

        self._provider = get_provider(config, self._reasoning_effort)
        logger.info(
            "Provider selected: %s for model %s (canonical=%s)",
            type(self._provider).__name__,
            config.model_name,
            config.canonical_model,
        )

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
                if attempt >= max_retries or not self._provider.should_retry(e):
                    self._raise_error(e)
                wait = min(90, 2 * (2**attempt))
                await asyncio.sleep(wait)

    async def _stream(self, messages: list[dict[str, Any]]) -> AsyncIterator[LLMResponse]:
        from strix.tools.registry import get_tools_definitions

        if self._provider.supports_prompt_caching():
            messages = self._provider.prepare_messages(messages)
        async for response in self._provider.generate_stream(
            messages=messages,
            tools=get_tools_definitions(),
            tool_choice="auto",
        ):
            yield response

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
        # Handles native tool-calling: assistant+tool_calls followed by tool role messages.
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
                i += 1
                continue

            # Regular message — pass through as-is (strip internal keys)
            api_msg = {"role": msg["role"], "content": msg.get("content", "")}
            messages.append(api_msg)
            i += 1

        if messages[-1].get("role") == "assistant" and not self.config.interactive:
            messages.append({"role": "user", "content": "<meta>Continue the task.</meta>"})

        return messages

    def _raise_error(self, e: Exception) -> None:
        from strix.telemetry import posthog

        posthog.error("llm_error", type(e).__name__)
        raise LLMRequestFailedError(f"LLM request failed: {type(e).__name__}", str(e)) from e

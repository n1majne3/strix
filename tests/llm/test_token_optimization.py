"""Tests for token optimization: lazy skill loading, conditional multi_agent_system, chunk_size tuning.

Verifies the three optimizations from M003/S02:
1. Lazy skill loading — subagents defer vulnerability/tooling/framework skills
2. Conditional multi_agent_system — only rendered for root agents
3. Memory compressor chunk_size=5 for better granularity
"""

from unittest.mock import MagicMock, patch

from strix.llm.config import LLMConfig
from strix.llm.llm import LLM
from strix.llm.memory_compressor import MemoryCompressor
from strix.skills import discover_skills, load_skills


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_config(
    skills: list[str] | None = None,
    scan_mode: str = "deep",
    is_whitebox: bool = False,
) -> MagicMock:
    """Build a mock LLMConfig with all attributes needed by LLM.__init__."""
    config = MagicMock(spec=LLMConfig)
    config.skills = list(skills or [])
    config.scan_mode = scan_mode
    config.is_whitebox = is_whitebox
    config.interactive = False
    config.system_prompt_context = {}
    config.litellm_model = "anthropic/claude-sonnet-4-20250514"
    config.model_name = "claude-sonnet-4-20250514"
    config.canonical_model = "anthropic/claude-sonnet-4-20250514"
    config.reasoning_effort = None
    return config


def _make_llm_with_real_prompt(config: MagicMock, agent_name: str = "StrixAgent") -> LLM:
    """Create an LLM whose _load_system_prompt actually renders the Jinja template.

    Patches get_provider and Config.get to avoid real API calls/config lookups.
    """
    with (
        patch("strix.llm.llm.get_provider") as mock_get_provider,
        patch("strix.llm.llm.Config.get", return_value=None),
    ):
        mock_provider = MagicMock()
        mock_get_provider.return_value = mock_provider
        llm = LLM(config, agent_name=agent_name)
    return llm


# ---------------------------------------------------------------------------
# 1. Lazy loading — subagent does NOT preload vulnerability skills
# ---------------------------------------------------------------------------


class TestLazySkillLoading:
    """Verify subagents skip non-essential skills in the system prompt."""

    def test_subagent_no_vuln_skills_in_prompt(self):
        config = _make_config(skills=["sql-injection", "xss"])
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        # sql-injection and xss are in the 'vulnerabilities' category — not essential.
        # Skills are wrapped in <skill_name> tags in the prompt.
        # Check that the full skill content block is absent.
        assert "<sql-injection>" not in prompt
        assert "<xss>" not in prompt

    def test_subagent_no_tooling_skills_in_prompt(self):
        config = _make_config(skills=["ffuf", "nmap"])
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        # tooling category is not essential — skill tags should be absent
        assert "<ffuf>" not in prompt
        assert "<nmap>" not in prompt

    def test_subagent_no_framework_skills_in_prompt(self):
        config = _make_config(skills=["fastapi", "nextjs"])
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        assert "<fastapi>" not in prompt
        assert "<nextjs>" not in prompt

    def test_root_agent_skill_is_essential(self):
        """root-agent stays marked essential in discovery metadata."""
        config = _make_config(skills=["root-agent"])
        llm = _make_llm_with_real_prompt(config)

        assert "root-agent" in llm._active_skills
        assert discover_skills()["root-agent"]["essential"] == "true"

    def test_root_agent_skill_content_in_prompt(self):
        """Root agent prompt includes the root-agent skill content."""
        config = _make_config(skills=["root-agent"])
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        # The root-agent skill has "Orchestration layer"
        assert "Orchestration layer" in prompt or "root-agent" in prompt.lower()

    def test_scan_mode_skills_are_not_marked_essential(self):
        """Scan-mode skills are conditional, not essential-by-frontmatter."""
        discovered = discover_skills()
        assert discovered["root-agent"]["essential"] == "true"
        assert discovered["quick"]["essential"] != "true"
        assert discovered["standard"]["essential"] != "true"
        assert discovered["deep"]["essential"] != "true"

    def test_get_skills_to_load_filters_deferred(self):
        """_get_skills_to_load returns only essential + force-loaded skills."""
        config = _make_config(skills=["sql-injection", "xss", "root-agent"])
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        # root-agent is essential; sql-injection and xss are deferred.
        assert "root-agent" in loaded
        assert "deep" in loaded
        assert "sql-injection" not in loaded
        assert "xss" not in loaded


# ---------------------------------------------------------------------------
# 2. add_skills (load_skill path) injects deferred skills correctly
# ---------------------------------------------------------------------------


class TestOnDemandSkillLoading:
    """Verify add_skills force-loads deferred skills into the prompt."""

    def test_add_skills_injects_deferred_content(self):
        config = _make_config(skills=[])
        llm = _make_llm_with_real_prompt(config)

        # Initially no sql-injection skill tag
        initial_prompt = llm.system_prompt
        assert "<sql-injection>" not in initial_prompt

        # Add sql-injection on demand
        added = llm.add_skills(["sql-injection"])
        assert "sql-injection" in added

        # Now the prompt should contain the sql-injection skill block
        updated_prompt = llm.system_prompt
        assert "<sql-injection>" in updated_prompt
        assert "SQL Injection" in updated_prompt

    def test_add_skills_tracks_force_loaded(self):
        config = _make_config(skills=[])
        llm = _make_llm_with_real_prompt(config)

        llm.add_skills(["ffuf", "nmap"])
        assert "ffuf" in llm._force_loaded_skills
        assert "nmap" in llm._force_loaded_skills

    def test_add_skills_idempotent(self):
        """Adding the same skill twice returns empty on second call."""
        config = _make_config(skills=[])
        llm = _make_llm_with_real_prompt(config)

        added1 = llm.add_skills(["sql-injection"])
        assert "sql-injection" in added1

        added2 = llm.add_skills(["sql-injection"])
        assert added2 == []

    def test_force_loaded_skills_in_get_skills_to_load(self):
        """After add_skills, the skill appears in _get_skills_to_load."""
        config = _make_config(skills=[])
        llm = _make_llm_with_real_prompt(config)

        llm.add_skills(["sql-injection"])
        loaded = llm._get_skills_to_load()
        assert "sql-injection" in loaded


# ---------------------------------------------------------------------------
# 3. Conditional multi_agent_system section
# ---------------------------------------------------------------------------


class TestConditionalMultiAgentSystem:
    """Verify multi_agent_system section is rendered only for root agents."""

    def test_subagent_no_multi_agent_system(self):
        config = _make_config(skills=[])  # No root-agent skill
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        assert "AGENT ISOLATION & SANDBOXING" not in prompt
        assert "<multi_agent_system>" not in prompt

    def test_root_agent_has_multi_agent_system(self):
        config = _make_config(skills=["root-agent"])
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        assert "<multi_agent_system>" in prompt
        assert "AGENT ISOLATION & SANDBOXING" in prompt

    def test_is_root_agent_derived_from_skills(self):
        """is_root_agent is True when root-agent is in active skills."""
        config_root = _make_config(skills=["root-agent"])
        llm_root = _make_llm_with_real_prompt(config_root)
        assert "root-agent" in llm_root._active_skills

        config_sub = _make_config(skills=["sql-injection"])
        llm_sub = _make_llm_with_real_prompt(config_sub)
        assert "root-agent" not in llm_sub._active_skills


# ---------------------------------------------------------------------------
# 4. Memory compressor chunk_size = 5
# ---------------------------------------------------------------------------


class TestMemoryCompressorChunkSize:
    """Verify memory compressor uses chunk_size=5."""

    def test_chunk_size_is_5(self):
        """The compress_history method should use chunk_size=5."""
        # Patch _summarize_messages to avoid real LLM calls and inspect chunk sizes
        with patch("strix.llm.memory_compressor._summarize_messages") as mock_summarize:
            mock_summarize.return_value = {
                "role": "user",
                "content": "<context_summary>summary</context_summary>",
            }
            # Patch token counting to force compression (exceed 90% of 100K)
            with patch("strix.llm.memory_compressor._get_message_tokens", return_value=95000):
                compressor = MemoryCompressor(model_name="anthropic/claude-sonnet-4-20250514")

                # Create 20 messages (more than MIN_RECENT_MESSAGES=15)
                messages = [
                    {"role": "user", "content": f"message {i}"} for i in range(20)
                ]

                result = compressor.compress_history(messages)

                # The old messages are those beyond the last 15
                # 20 total - 15 recent = 5 old messages
                # With chunk_size=5, that's 1 chunk → 1 summarize call
                assert mock_summarize.called
                # Verify the chunk passed has exactly 5 messages
                chunk_arg = mock_summarize.call_args[0][0]
                assert len(chunk_arg) == 5

    def test_multiple_chunks_with_chunk_size_5(self):
        """With 25 old messages and chunk_size=5, we get 5 summarize calls."""
        with patch("strix.llm.memory_compressor._summarize_messages") as mock_summarize:
            mock_summarize.return_value = {
                "role": "user",
                "content": "<context_summary>summary</context_summary>",
            }
            with patch("strix.llm.memory_compressor._get_message_tokens", return_value=95000):
                compressor = MemoryCompressor(model_name="anthropic/claude-sonnet-4-20250514")

                # 40 messages total → 40 - 15 recent = 25 old → 5 chunks of 5
                messages = [
                    {"role": "user", "content": f"message {i}"} for i in range(40)
                ]

                result = compressor.compress_history(messages)

                assert mock_summarize.call_count == 5
                # Each call should receive exactly 5 messages
                for call in mock_summarize.call_args_list:
                    chunk = call[0][0]
                    assert len(chunk) == 5


# ---------------------------------------------------------------------------
# 5. Scan mode skill always loaded
# ---------------------------------------------------------------------------


class TestScanModeAlwaysLoaded:
    """Verify scan_modes skill is always included regardless of lazy loading."""

    def test_scan_mode_deep_always_in_skills_to_load(self):
        config = _make_config(skills=["sql-injection", "xss"], scan_mode="deep")
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        assert "deep" in loaded

    def test_scan_mode_quick_always_in_skills_to_load(self):
        config = _make_config(skills=["sql-injection"], scan_mode="quick")
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        assert "quick" in loaded

    def test_scan_mode_content_in_prompt(self):
        config = _make_config(skills=["sql-injection"], scan_mode="deep")
        llm = _make_llm_with_real_prompt(config)

        prompt = llm.system_prompt
        # The deep.md skill should be present
        assert "deep" in prompt.lower() or "exhaustive" in prompt.lower()


# ---------------------------------------------------------------------------
# 6. Whitebox coordination skills
# ---------------------------------------------------------------------------


class TestWhiteboxCoordinationSkills:
    """Verify source_aware_whitebox skill is loaded when is_whitebox=True."""

    def test_whitebox_skills_included(self):
        config = _make_config(skills=[], is_whitebox=True)
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        assert "source-aware-whitebox" in loaded
        assert "source-aware-sast" in loaded

    def test_whitebox_skills_not_included_for_blackbox(self):
        config = _make_config(skills=[], is_whitebox=False)
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        assert "source-aware-whitebox" not in loaded
        assert "source-aware-sast" not in loaded

    def test_source_aware_whitebox_recommends_valid_skill_name(self):
        skill_content = load_skills(["source-aware-whitebox"])["source-aware-whitebox"]
        assert "`source-aware-sast`" in skill_content
        assert "`source_aware_sast`" not in skill_content


# ---------------------------------------------------------------------------
# 7. Baseline measurement test
# ---------------------------------------------------------------------------


class TestBaselineMeasurements:
    """Measure system prompt sizes and verify subagent is smaller than root agent."""

    def test_subagent_prompt_smaller_than_root(self):
        """Subagent prompt should be significantly smaller than root agent prompt."""
        # Root agent: has root-agent skill + multi_agent_system section
        config_root = _make_config(
            skills=["root-agent", "sql-injection", "xss", "nmap", "ffuf"],
            scan_mode="deep",
        )
        llm_root = _make_llm_with_real_prompt(config_root)
        root_prompt = llm_root.system_prompt

        # Subagent: no root-agent skill, deferred vuln skills
        config_sub = _make_config(
            skills=["sql-injection", "xss", "nmap", "ffuf"],
            scan_mode="deep",
        )
        llm_sub = _make_llm_with_real_prompt(config_sub)
        sub_prompt = llm_sub.system_prompt

        root_chars = len(root_prompt)
        sub_chars = len(sub_prompt)

        # Log sizes for visibility
        print(f"\nRoot agent prompt: {root_chars} chars")
        print(f"Subagent prompt: {sub_chars} chars")
        print(f"Savings: {root_chars - sub_chars} chars ({100 * (root_chars - sub_chars) / max(root_chars, 1):.1f}%)")

        # Subagent prompt must be smaller — root has multi_agent_system section
        assert sub_chars < root_chars, (
            f"Subagent prompt ({sub_chars} chars) should be smaller than "
            f"root agent prompt ({root_chars} chars)"
        )

        # Savings should be meaningful — at least the multi_agent_system block
        # The block is ~130 lines, easily several KB
        assert (root_chars - sub_chars) > 1000, (
            f"Savings ({root_chars - sub_chars} chars) too small — expected > 1000"
        )

    def test_subagent_deferred_skills_size(self):
        """Measure how much content is deferred for a typical subagent."""
        # Subagent with lots of non-essential skills
        config_deferred = _make_config(
            skills=["sql-injection", "xss", "ffuf", "nmap", "fastapi", "nextjs"],
            scan_mode="deep",
        )
        llm_deferred = _make_llm_with_real_prompt(config_deferred)
        deferred_prompt = llm_deferred.system_prompt

        # Same config but with all skills force-loaded
        config_all = _make_config(
            skills=["sql-injection", "xss", "ffuf", "nmap", "fastapi", "nextjs"],
            scan_mode="deep",
        )
        llm_all = _make_llm_with_real_prompt(config_all)
        llm_all.add_skills(["sql-injection", "xss", "ffuf", "nmap", "fastapi", "nextjs"])
        full_prompt = llm_all.system_prompt

        deferred_chars = len(deferred_prompt)
        full_chars = len(full_prompt)

        print(f"\nDeferred (lazy) prompt: {deferred_chars} chars")
        print(f"Full (all loaded) prompt: {full_chars} chars")
        print(f"Savings from deferral: {full_chars - deferred_chars} chars ({100 * (full_chars - deferred_chars) / max(full_chars, 1):.1f}%)")

        # If all skills were already in _active_skills, they get filtered by essential check
        # The deferred prompt should be smaller than or equal to the full prompt
        # (equal if the skills were already in active but filtered)
        assert deferred_chars <= full_chars


# ---------------------------------------------------------------------------
# 8. Integration: full skill filter pipeline
# ---------------------------------------------------------------------------


class TestSkillFilterPipeline:
    """End-to-end tests for the skill filtering pipeline."""

    def test_discover_skills_uses_hyphenated_identifiers(self):
        """Discovery exposes the migrated hyphenated skill IDs."""
        discovered = discover_skills()
        assert "root-agent" in discovered
        assert "sql-injection" in discovered
        assert "root_agent" not in discovered
        assert "sql_injection" not in discovered

    def test_mixed_skills_loads_only_essential_plus_scan_mode(self):
        """Mixed skill list: only essential + scan_mode are loaded initially."""
        config = _make_config(
            skills=["root-agent", "sql-injection", "xss", "ffuf"],
            scan_mode="standard",
        )
        llm = _make_llm_with_real_prompt(config)

        loaded = llm._get_skills_to_load()
        # root-agent is essential; sql-injection, xss, ffuf are not.
        assert "root-agent" in loaded
        assert "standard" in loaded
        assert "sql-injection" not in loaded
        assert "xss" not in loaded
        assert "ffuf" not in loaded

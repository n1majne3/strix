"""Regression test: assert no XML tool-calling harness patterns remain in production code.

This test scans every ``*.py`` file under ``strix/`` for residual XML
tool-calling patterns that were removed in M001/S07.  If any are found
outside the explicitly-allowlisted exemptions, the test fails with a
clear report of which file:line contains the violation.

The patterns checked:
    - ``<function=``         (legacy XML tool-call open tag)
    - ``<tool_result>``      (legacy XML tool-result tag)
    - ``_schema.xml``        (Pydantic XML schema export)
    - ``parse_tool_invocations``  (old XML parser function)
    - ``get_tools_prompt``   (old XML prompt generator)
    - ``xmltodict``          (removed dependency)
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Allowlist: (file_path_suffix, pattern) pairs that are LEGITIMATE and must
# not trigger a failure.  Keep this list tight — new entries should have a
# comment explaining why.
# ---------------------------------------------------------------------------
ALLOWLIST: list[tuple[str, str]] = [
    # strix/llm/utils.py — defensive stripping of stray XML that LLMs may
    # emit in text output.  These are NOT the XML tool-calling harness; they
    # are safety-net utilities used by base_agent.py and agent_message_renderer.py.
    ("strix/llm/utils.py", "<function="),
]

PATTERNS = (
    "<function=",
    "<tool_result>",
    "_schema.xml",
    "parse_tool_invocations",
    "get_tools_prompt",
    "xmltodict",
)

PRODUCTION_ROOT = Path("strix")


def test_no_xml_harness_remains_in_production_code() -> None:
    violations: list[str] = []

    for py_file in sorted(PRODUCTION_ROOT.rglob("*.py")):
        # Skip __pycache__ bytecode stubs
        if "__pycache__" in str(py_file):
            continue

        file_suffix = str(py_file)

        for lineno, line in enumerate(py_file.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = line.lstrip()
            # Skip comment-only lines and docstrings (heuristic: lines that
            # are purely documentation don't count as *code* violations).
            # But we still flag them if they are inside executable code paths.

            for pattern in PATTERNS:
                if pattern not in line:
                    continue

                # Check allowlist — only exempt the exact (file, pattern) pair
                if any(
                    file_suffix.endswith(awl_file) and pattern == awl_pattern
                    for awl_file, awl_pattern in ALLOWLIST
                ):
                    continue

                violations.append(f"{file_suffix}:{lineno}: found '{pattern}' in: {stripped.rstrip()}")

    if violations:
        msg = (
            "XML tool-calling harness patterns found in production code.\n"
            "If any of these are intentional, add them to ALLOWLIST with a comment.\n\n"
            + "\n".join(violations)
        )
        raise AssertionError(msg)

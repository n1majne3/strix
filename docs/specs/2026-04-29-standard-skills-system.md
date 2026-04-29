# Standard Skills System

## Problem

Strix's skill system uses a custom format that differs from the standard adopted by Claude Code, OpenCode, and similar tools. The current system has:

- Flat files named `<skill>.md` in category subdirectories (`skills/<category>/<name>.md`)
- A custom Python loader with hardcoded category constants (`_EXCLUDED_CATEGORIES`, `_ESSENTIAL_CATEGORIES`)
- An unused XML schema system inherited from upstream (never wired up in the fork)
- A dead `generate_skills_description()` function
- The `strix/prompts/` directory with a Jinja template (`nosql_injection.jinja`) that nothing loads

The standard format (Claude Code / OpenCode) uses directory-based skills with a fixed `SKILL.md` filename and YAML frontmatter. Adopting this format makes skills portable and discoverable by any tool that understands the convention.

## Design

### Directory Structure

```
strix/skills/
  __init__.py
  xss/SKILL.md
  sql-injection/SKILL.md
  kubernetes/SKILL.md
  nmap/SKILL.md
  quick/SKILL.md
  standard/SKILL.md
  deep/SKILL.md
  root-agent/SKILL.md
  source-aware-whitebox/SKILL.md
  source-aware-sast/SKILL.md
  ...
```

Each skill is a directory. The core file is always `SKILL.md`. Directory name is the skill identifier, using hyphens (not underscores).

### SKILL.md Format

```yaml
---
name: sql-injection
description: SQL injection testing covering union, blind, error-based, and ORM bypass techniques
category: vulnerabilities
---
# SQL Injection

[content...]
```

Frontmatter fields:

| Field | Required | Description |
|-------|----------|-------------|
| `name` | yes | Must match directory name |
| `description` | yes | One-line summary for tool descriptions and skill listings |
| `category` | yes | Classification: `vulnerabilities`, `tooling`, `frameworks`, `cloud`, `technologies`, `protocols`, `ctf`, `scan-modes`, `coordination`, `custom` |
| `essential` | no | If `true`, loaded automatically at startup (default: not set / false) |

### Supporting Files

Skill directories may contain additional `.md` files alongside `SKILL.md` for supplementary reference material. Only `SKILL.md` is loaded as the primary skill content.

### Discovery

`discover_skills()` scans `strix/skills/*/SKILL.md` using `Path.rglob("SKILL.md")`. For each found file:

1. Parse YAML frontmatter to extract `name`, `description`, `category`, `essential`
2. Build index: `{skill_name: {"path", "description", "category", "essential"}}`
3. Skip directories starting with `_` or `.`

### Loading

`load_skills(skill_names: list[str]) -> dict[str, str]`:

1. Look up each name in the discovery index
2. Read `SKILL.md`, strip frontmatter, return content
3. Returns `{skill_name: content_without_frontmatter}`

### Startup Loading

In `llm.py`, `_get_skills_to_load()`:

1. Load all skills with `essential: true` in frontmatter (e.g., `root-agent`, `source-aware-whitebox`, `source-aware-sast`)
2. Load the scan mode skill matching `config.scan_mode` by name (`quick` / `standard` / `deep`) — these are NOT marked essential, they are loaded conditionally
3. Deduplicate and return

Replaces the current `_ESSENTIAL_CATEGORIES` set and the `f"scan_modes/{self.config.scan_mode}"` pattern. The `essential` flag means "always load at startup." Scan mode skills are loaded by explicit name match against config, not by the essential flag.

### On-Demand Loading

The `load_skill` tool remains unchanged. Agent calls `load_skill("sql-injection")` at runtime, which calls `llm.add_skills()`, reads the SKILL.md, and rebuilds the system prompt.

`generate_skills_description()` returns a comma-separated list of all non-essential skill names for embedding in the `load_skill` tool description. This replaces the dead code version.

### Cleanup

Remove:

- `strix/prompts/vulnerabilities/nosql_injection.jinja` (convert to `strix/skills/nosql-injection/SKILL.md`, then delete original)
- Upstream XML schema system references (already removed in fork)
- `_EXCLUDED_CATEGORIES` and `_ESSENTIAL_CATEGORIES` constants from `__init__.py` and `llm.py`
- Old category subdirectories after migration

## Files to Modify

| File | Change |
|------|--------|
| `strix/skills/__init__.py` | Rewrite: discovery/loading based on `*/SKILL.md` |
| `strix/llm/llm.py` | Update `_get_skills_to_load()` to use new loader |
| `strix/skills/*/SKILL.md` | Migrate 51 skills (rename dirs, rename files, add frontmatter fields) |
| `strix/skills/README.md` | Update documentation |
| `strix/prompts/vulnerabilities/nosql_injection.jinja` | Convert to `strix/skills/nosql-injection/SKILL.md` or delete |

## Migration

For each existing skill `strix/skills/<category>/<name>.md`:

1. Create directory `strix/skills/<name-hyphenated>/`
2. Move file as `SKILL.md`
3. Add `category` field to frontmatter
4. Add `essential: true` if in essential categories (`coordination`, `custom`, `scan-modes` but only matching scan_mode at runtime)
5. Convert underscores in directory name to hyphens

Special cases:
- `scan_modes/quick.md` -> `quick/SKILL.md` (not essential; loaded by config.scan_mode match)
- `scan_modes/standard.md` -> `standard/SKILL.md` (not essential; loaded by config.scan_mode match)
- `scan_modes/deep.md` -> `deep/SKILL.md` (not essential; loaded by config.scan_mode match)
- `coordination/root_agent.md` -> `root-agent/SKILL.md` (essential: true)
- `coordination/source_aware_whitebox.md` -> `source-aware-whitebox/SKILL.md` (essential: true)
- `custom/source_aware_sast.md` -> `source-aware-sast/SKILL.md` (essential: true)
- `vulnerabilities/sql_injection.md` -> `sql-injection/SKILL.md`
- `prompts/vulnerabilities/nosql_injection.jinja` -> `nosql-injection/SKILL.md` (convert to standard format)

## Validation

After migration:

1. `discover_skills()` returns all 51+ skills
2. `load_skills(["xss"])` returns content without frontmatter
3. `get_available_skills()` returns skills grouped by category
4. `generate_skills_description()` returns comma-separated names
5. Startup loads essential + matching scan mode skill
6. `load_skill` tool works for on-demand loading

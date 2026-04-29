# Standard Skills System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate Strix's 51 skills from `skills/<category>/<name>.md` to the standard `skills/<name>/SKILL.md` directory format, rewriting the loader and updating all callers.

**Architecture:** Replace the category-directory + custom loader system with flat directory-per-skill layout using `SKILL.md`. Discovery scans `*/SKILL.md` via `Path.rglob`. Frontmatter drives categorization and essential flag. `llm.py` loads essential + scan-mode skills at startup, other skills on-demand.

**Tech Stack:** Python 3.10+, pathlib, re (YAML frontmatter parsing — no new dependencies)

---

### Task 1: Rewrite `strix/skills/__init__.py`

**Files:**
- Modify: `strix/skills/__init__.py`

- [ ] **Step 1: Replace the entire file with the new loader**

```python
import re
from pathlib import Path

from strix.utils.resource_paths import get_strix_resource_path

_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SKILL_FILENAME = "SKILL.md"


def _parse_frontmatter(content: str) -> dict[str, str]:
    """Extract key:value pairs from YAML frontmatter."""
    match = _FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}
    meta: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()
    return meta


def _strip_frontmatter(content: str) -> str:
    return _FRONTMATTER_PATTERN.sub("", content).lstrip()


def discover_skills(skills_dir: Path | None = None) -> dict[str, dict[str, str]]:
    """Scan for SKILL.md files and build an index.

    Returns {skill_name: {"path": relative_path, "description": str, "category": str, "essential": str}}.
    """
    if skills_dir is None:
        skills_dir = get_strix_resource_path("skills")

    if not skills_dir.exists():
        return {}

    discovered: dict[str, dict[str, str]] = {}
    for skill_file in sorted(skills_dir.rglob(_SKILL_FILENAME)):
        rel = skill_file.relative_to(skills_dir)
        skill_name = rel.parent.name

        if skill_name.startswith("_") or skill_name.startswith("."):
            continue

        content = skill_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)

        discovered[skill_name] = {
            "path": str(rel),
            "description": meta.get("description", ""),
            "category": meta.get("category", ""),
            "essential": meta.get("essential", ""),
        }

    return discovered


def get_available_skills() -> dict[str, list[str]]:
    """Return {category: [skill_names]} for non-essential skills."""
    discovered = discover_skills()
    by_category: dict[str, list[str]] = {}
    for name, info in discovered.items():
        if info.get("essential") == "true":
            continue
        cat = info["category"] or "uncategorized"
        by_category.setdefault(cat, []).append(name)
    return {cat: sorted(names) for cat, names in sorted(by_category.items())}


def get_all_skill_names() -> set[str]:
    return set(discover_skills().keys())


def validate_skill_names(skill_names: list[str]) -> dict[str, list[str]]:
    available = get_all_skill_names()
    return {
        "valid": [s for s in skill_names if s in available],
        "invalid": [s for s in skill_names if s not in available],
    }


def parse_skill_list(skills: str | None) -> list[str]:
    if not skills:
        return []
    return [s.strip() for s in skills.split(",") if s.strip()]


def validate_requested_skills(skill_list: list[str], max_skills: int = 5) -> str | None:
    if len(skill_list) > max_skills:
        return "Cannot specify more than 5 skills for an agent (use comma-separated format)"
    if not skill_list:
        return None
    validation = validate_skill_names(skill_list)
    if validation["invalid"]:
        available = list(get_all_skill_names())
        return (
            f"Invalid skills: {validation['invalid']}. "
            f"Available skills: {', '.join(available)}"
        )
    return None


def generate_skills_description() -> str:
    """Return comma-separated non-essential skill names for tool descriptions."""
    discovered = discover_skills()
    names = sorted(
        n for n, info in discovered.items() if info.get("essential") != "true"
    )
    return ", ".join(names) if names else "No skills available"


def load_skills(skill_names: list[str]) -> dict[str, str]:
    """Load skill content by name. Returns {skill_name: content_without_frontmatter}."""
    import logging

    logger = logging.getLogger(__name__)
    skills_dir = get_strix_resource_path("skills")
    discovered = discover_skills(skills_dir)
    skill_content: dict[str, str] = {}

    for skill_name in skill_names:
        info = discovered.get(skill_name)
        if not info:
            logger.warning(f"Skill not found: {skill_name}")
            continue
        try:
            full_path = skills_dir / info["path"]
            content = full_path.read_text(encoding="utf-8")
            skill_content[skill_name] = _strip_frontmatter(content)
            logger.info(f"Loaded skill: {skill_name}")
        except (FileNotFoundError, OSError) as e:
            logger.warning(f"Failed to load skill {skill_name}: {e}")

    return skill_content
```

- [ ] **Step 2: Commit**

```bash
git add strix/skills/__init__.py
git commit -m "refactor: rewrite skills loader for standard SKILL.md format"
```

---

### Task 2: Migrate all skill files to standard directory layout

**Files:**
- Create: 51 directories under `strix/skills/<name>/SKILL.md`
- Delete: all `strix/skills/<category>/<name>.md` files and empty category dirs

- [ ] **Step 1: Run the migration script**

```bash
cd /Users/benjamin/tools/strix

# Mapping of old category/name to new name (with hyphens) and metadata
python3 -c "
import os, re

FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

CATEGORY_MAP = {
    'scan_modes': 'scan-modes',
    'vulnerabilities': 'vulnerabilities',
    'tooling': 'tooling',
    'frameworks': 'frameworks',
    'technologies': 'technologies',
    'protocols': 'protocols',
    'cloud': 'cloud',
    'ctf': 'ctf',
    'coordination': 'coordination',
    'custom': 'custom',
    'reconnaissance': 'reconnaissance',
}

ESSENTIAL = {'root-agent', 'source-aware-whitebox', 'source-aware-sast'}

skills_dir = 'strix/skills'
migrated = 0

for category_dir in sorted(os.listdir(skills_dir)):
    cat_path = os.path.join(skills_dir, category_dir)
    if not os.path.isdir(cat_path) or category_dir.startswith('_') or category_dir.startswith('.'):
        continue
    if category_dir not in CATEGORY_MAP:
        continue

    for filename in sorted(os.listdir(cat_path)):
        if not filename.endswith('.md'):
            continue
        filepath = os.path.join(cat_path, filename)
        old_name = filename[:-3]  # strip .md
        new_name = old_name.replace('_', '-')
        category = CATEGORY_MAP[category_dir]

        # Read content
        with open(filepath) as f:
            content = f.read()

        # Update frontmatter
        match = FRONTMATTER_RE.match(content)
        if match:
            fm = match.group(1)
            # Update name to use hyphens
            fm = re.sub(r'^name:.*$', f'name: {new_name}', fm, flags=re.MULTILINE)
            # Add category if missing
            if 'category:' not in fm:
                fm += f'\ncategory: {category}'
            # Add essential if needed
            if new_name in ESSENTIAL and 'essential:' not in fm:
                fm += '\nessential: true'
            # Rebuild content
            content = f'---\n{fm}\n---\n{content[match.end():]}'

        # Create new directory and SKILL.md
        new_dir = os.path.join(skills_dir, new_name)
        os.makedirs(new_dir, exist_ok=True)
        new_path = os.path.join(new_dir, 'SKILL.md')
        with open(new_path, 'w') as f:
            f.write(content)

        migrated += 1
        print(f'{filepath} -> {new_path}')

print(f'\nMigrated {migrated} skills')
"
```

Expected: "Migrated 51 skills"

- [ ] **Step 2: Convert nosql_injection.jinja to standard skill**

```bash
mkdir -p strix/skills/nosql-injection
```

Create `strix/skills/nosql-injection/SKILL.md`. The source is `strix/prompts/vulnerabilities/nosql_injection.jinja` — it has structured XML tags (`<nosql_injection_guide>`, `<mongodb>`, `<scope>`, etc.) that need to be converted to standard markdown.

```bash
python3 -c "
import re

with open('strix/prompts/vulnerabilities/nosql_injection.jinja') as f:
    raw = f.read()

# Remove outer XML wrapper
raw = raw.strip()
if raw.startswith('<nosql_injection_guide>'):
    raw = raw[len('<nosql_injection_guide>'):]
if raw.endswith('</nosql_injection_guide>'):
    raw = raw[:-len('</nosql_injection_guide>')]

# Convert XML section tags to markdown headers
# <title>X</title> -> already fine, will be handled
# <scope> -> ## Scope
# <methodology> -> ## Methodology
# <mongodb> -> ### MongoDB
# etc.
tag_map = {
    'title': '# ',
    'critical': '> **CRITICAL:** ',
    'scope': '## Scope',
    'methodology': '## Methodology',
    'injection_surfaces': '## Injection Surfaces',
    'detection_channels': '## Detection Channels',
    'dbms_primitives': '## DBMS Primitives',
    'mongodb': '### MongoDB',
    'couchdb': '### CouchDB',
    'redis': '### Redis',
    'cassandra': '### Cassandra',
    'neo4j': '### Neo4j',
    'authentication_bypass': '## Authentication Bypass',
    'mongodb_operators': '### MongoDB Operators',
    'query_string_injection': '### Query String Injection',
    'data_extraction': '## Data Extraction',
    'regex_extraction': '### Regex Extraction',
    'boolean_extraction': '### Boolean Extraction',
    'javascript_extraction': '### JavaScript Extraction',
    'aggregation_based': '### Aggregation Based',
    'javascript_injection': '## JavaScript Injection',
    'where_clause': '### \$where Clause',
    'function_operator': '### \$function Operator',
    'mapreduce': '### MapReduce',
    'odm_and_framework_issues': '## ODM & Framework Issues',
    'mongoose': '### Mongoose',
    'morphia_java': '### Morphia (Java)',
    'pymongo': '### PyMongo',
    'waf_and_filter_bypasses': '## WAF & Filter Bypasses',
    'encoding_tricks': '### Encoding Tricks',
    'operator_alternatives': '### Operator Alternatives',
    'structure_manipulation': '### Structure Manipulation',
    'comment_injection': '### Comment Injection',
    'blind_extraction': '## Blind Extraction',
    'binary_search': '### Binary Search',
    'timing_oracle': '### Timing Oracle',
    'response_differential': '### Response Differential',
    'server_side_injection': '## Server-Side Injection',
    'ssjs_mongodb': '### SSJS (MongoDB)',
    'dos_attacks': '### DoS Attacks',
    'graphql_nosql': '## GraphQL + NoSQL',
    'validation': '## Validation',
    'false_positives': '## False Positives',
    'impact': '## Impact',
    'pro_tips': '## Pro Tips',
    'remember': '> **Remember:** ',
}

# Convert XML open/close tags to markdown
for tag, replacement in sorted(tag_map.items(), key=lambda x: -len(x[0])):
    raw = re.sub(rf'<{tag}>', replacement, raw)
    raw = re.sub(rf'</{tag}>', '', raw)

# Clean up remaining XML tags not in map
raw = re.sub(r'</?[a-z_]+>', '', raw)

# Clean up {% raw %}/{% endraw %} Jinja tags
raw = raw.replace('{% raw %}', '').replace('{% endraw %}', '')

# Strip excessive blank lines
raw = re.sub(r'\n{3,}', '\n\n', raw)

# Add frontmatter
frontmatter = '''---
name: nosql-injection
description: NoSQL injection testing covering MongoDB, CouchDB, Redis, Cassandra, and Neo4j attack vectors
category: vulnerabilities
---

'''
content = frontmatter + raw.strip() + '\n'

with open('strix/skills/nosql-injection/SKILL.md', 'w') as f:
    f.write(content)

print('Converted nosql_injection.jinja -> nosql-injection/SKILL.md')
"
```

- [ ] **Step 3: Remove old category directories and prompts directory**

```bash
rm -rf strix/skills/scan_modes strix/skills/vulnerabilities strix/skills/tooling \
       strix/skills/frameworks strix/skills/technologies strix/skills/protocols \
       strix/skills/cloud strix/skills/ctf strix/skills/coordination \
       strix/skills/custom strix/skills/reconnaissance
rm -rf strix/prompts
```

- [ ] **Step 4: Verify migration**

```bash
find strix/skills -name "SKILL.md" | wc -l
```

Expected: 52 (51 migrated + nosql-injection)

```bash
find strix/skills -maxdepth 1 -type d | wc -l
```

Expected: 53 (52 skill dirs + the skills dir itself)

- [ ] **Step 5: Commit**

```bash
git add -A strix/skills/ strix/prompts/
git commit -m "refactor: migrate skills to standard SKILL.md directory format"
```

---

### Task 3: Update `strix/llm/llm.py`

**Files:**
- Modify: `strix/llm/llm.py:17-140`

- [ ] **Step 1: Remove `_ESSENTIAL_CATEGORIES` constant and `_is_essential_skill` method, rewrite `_get_skills_to_load`**

Replace lines 17-20 (the `_ESSENTIAL_CATEGORIES` constant) and lines 96-99 (`_is_essential_skill`) with nothing. Replace `_get_skills_to_load` (lines 101-140) with:

```python
def _get_skills_to_load(self) -> list[str]:
    from strix.skills import discover_skills

    discovered = discover_skills()

    # Essential skills (marked essential: true in frontmatter)
    essential_skills = [
        name for name, info in discovered.items()
        if info.get("essential") == "true"
    ]

    # Force-loaded skills (on-demand via load_skill tool)
    forced_skills = [
        s for s in self._force_loaded_skills
    ]

    # Active skills from config
    active_essential = [
        s for s in self._active_skills
        if discovered.get(s, {}).get("essential") == "true"
    ]

    # Build ordered list
    ordered: list[str] = []
    seen: set[str] = set()
    for name in active_essential + essential_skills + forced_skills:
        if name not in seen:
            ordered.append(name)
            seen.add(name)

    # Conditional: scan mode skill
    scan_mode = self.config.scan_mode
    if scan_mode and scan_mode not in seen:
        ordered.append(scan_mode)
        seen.add(scan_mode)

    # Conditional: whitebox skills (loaded by essential flag, but keep explicit
    # fallback if not marked essential)
    if self.config.is_whitebox:
        for wb in ("source-aware-whitebox", "source-aware-sast"):
            if wb not in seen and wb in discovered:
                ordered.append(wb)
                seen.add(wb)

    logger.info(
        "Skill loading: %d essential, %d forced, scan_mode=%s",
        len([s for s in ordered if discovered.get(s, {}).get("essential") == "true"]),
        len([s for s in ordered if s in self._force_loaded_skills]),
        scan_mode,
    )

    return ordered
```

Also add the import at the top — no changes needed since `load_skills` is already imported from `strix.skills`.

- [ ] **Step 2: Update `is_root_agent` check in `_load_system_prompt`**

Line 89: `"root_agent" in self._active_skills` → `"root-agent" in self._active_skills` (hyphen).

```python
is_root_agent=("root-agent" in self._active_skills),
```

- [ ] **Step 3: Commit**

```bash
git add strix/llm/llm.py
git commit -m "refactor: update llm.py to use new skills loader with frontmatter-driven essential flag"
```

---

### Task 4: Update system prompt skill name references

**Files:**
- Modify: `strix/agents/StrixAgent/system_prompt.jinja:335-342`

- [ ] **Step 1: Update skill names from underscores to hyphens**

Lines 335-342 currently have:

```
- "SQLi Validation Agent" with skills: sql_injection
- "XSS Discovery Agent" with skills: xss
- "Auth Testing Agent" with skills: authentication_jwt, business_logic
- "SSRF + XXE Agent" with skills: ssrf, xxe, rce (related attack vectors)

- "General Web Testing Agent" with skills: sql_injection, xss, csrf, ssrf, authentication_jwt (too broad)
```

Change to:

```
- "SQLi Validation Agent" with skills: sql-injection
- "XSS Discovery Agent" with skills: xss
- "Auth Testing Agent" with skills: authentication-jwt, business-logic
- "SSRF + XXE Agent" with skills: ssrf, xxe, rce (related attack vectors)

- "General Web Testing Agent" with skills: sql-injection, xss, csrf, ssrf, authentication-jwt (too broad)
```

- [ ] **Step 2: Commit**

```bash
git add strix/agents/StrixAgent/system_prompt.jinja
git commit -m "fix: update skill names to hyphen format in system prompt"
```

---

### Task 5: Update existing tests

**Files:**
- Modify: `tests/tools/test_load_skill_tool.py:39,58,130`

- [ ] **Step 1: Update skill names in tests**

Line 39: `"ffuf,xss"` — no change needed (no underscores).
Line 58: `"nmap"` — no change needed.
Line 130: `"xss,sql_injection"` → change to `"xss,sql-injection"`

```python
result = load_skill_actions.load_skill(state, "xss,sql-injection")
```

Also line 134: `assert result["loaded_skills"] == ["xss", "sql-injection"]`
And line 136: `assert state.context["loaded_skills"] == ["sql-injection", "xss"]`

- [ ] **Step 2: Commit**

```bash
git add tests/tools/test_load_skill_tool.py
git commit -m "fix: update skill names to hyphen format in tests"
```

---

### Task 6: End-to-end validation

**Files:** none

- [ ] **Step 1: Verify discovery works**

```bash
cd /Users/benjamin/tools/strix
python3 -c "
from strix.skills import discover_skills, get_available_skills, load_skills, generate_skills_description

discovered = discover_skills()
print(f'Discovered: {len(discovered)} skills')
print(f'Categories: {dict((k, len(v)) for k, v in get_available_skills().items())}')
print(f'Essential: {[n for n, i in discovered.items() if i.get(\"essential\") == \"true\"]}')
print(f'Description: {generate_skills_description()[:200]}...')
"
```

Expected: 52 skills discovered, categories populated, 3 essential skills (root-agent, source-aware-whitebox, source-aware-sast).

- [ ] **Step 2: Verify load_skills works**

```bash
python3 -c "
from strix.skills import load_skills
content = load_skills(['xss', 'sql-injection', 'quick'])
for name, text in content.items():
    print(f'{name}: {len(text)} chars, starts with: {text[:60]}...')
"
```

Expected: 3 skills loaded, each with content starting with the markdown header (frontmatter stripped).

- [ ] **Step 3: Run existing tests**

```bash
cd /Users/benjamin/tools/strix
python3 -m pytest tests/tools/test_load_skill_tool.py -v
```

Expected: All tests pass.

- [ ] **Step 4: Commit final state if any fixes were needed**

---

### Task 7: Update skills README

**Files:**
- Modify: `strix/skills/README.md`

- [ ] **Step 1: Update README to reflect new structure**

Replace the README with:

```markdown
# Strix Skills

Skills are specialized knowledge packages in standard `SKILL.md` format.

## Structure

Each skill is a directory containing a `SKILL.md` file:

\`\`\`
strix/skills/
  xss/SKILL.md
  sql-injection/SKILL.md
  kubernetes/SKILL.md
\`\`\`

## Format

\`\`\`yaml
---
name: sql-injection
description: One-line description
category: vulnerabilities
essential: true          # optional; auto-loads at startup
---

# Skill Title

Content here...
\`\`\`

**Frontmatter fields:**
- `name` — must match directory name, use hyphens
- `description` — one-line summary
- `category` — vulnerabilities, tooling, frameworks, cloud, technologies, protocols, ctf, scan-modes, coordination, custom
- `essential` — set `true` to auto-load at startup (omit for on-demand skills)

## Categories

| Category | Description |
|----------|-------------|
| vulnerabilities | SQL injection, XSS, SSRF, etc. |
| tooling | nmap, nuclei, ffuf, etc. |
| frameworks | FastAPI, Next.js, NestJS |
| cloud | Kubernetes, AWS, GCP |
| technologies | Supabase, Firebase |
| protocols | GraphQL |
| ctf | CTF challenge types |
| scan-modes | quick, standard, deep |
| coordination | Root agent orchestration |
| custom | User-contributed skills |

## Creating Skills

1. Create directory: `strix/skills/<name>/`
2. Add `SKILL.md` with frontmatter and content
3. Set `category` to the appropriate classification
4. Set `essential: true` only if the skill must load at startup

Skills are discovered automatically. No registration needed.
```

- [ ] **Step 2: Commit**

```bash
git add strix/skills/README.md
git commit -m "docs: update skills README for standard SKILL.md format"
```

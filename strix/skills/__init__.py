import re
from pathlib import Path

from strix.utils.resource_paths import get_strix_resource_path

_FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_SKILL_FILENAME = "SKILL.md"


def _parse_frontmatter(content: str) -> dict[str, str]:
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
    discovered = discover_skills()
    names = sorted(
        n for n, info in discovered.items() if info.get("essential") != "true"
    )
    return ", ".join(names) if names else "No skills available"


def load_skills(skill_names: list[str]) -> dict[str, str]:
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

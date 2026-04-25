import inspect
import logging
import os
from collections.abc import Callable
from functools import wraps
from inspect import signature
from pathlib import Path
from typing import Any, get_type_hints

import defusedxml.ElementTree as DefusedET

from strix.utils.resource_paths import get_strix_resource_path


tools: list[dict[str, Any]] = []
_tools_by_name: dict[str, Callable[..., Any]] = {}
_tool_param_schemas: dict[str, dict[str, Any]] = {}
logger = logging.getLogger(__name__)


class ImplementedInClientSideOnlyError(Exception):
    def __init__(
        self,
        message: str = "This tool is implemented in the client side only",
    ) -> None:
        self.message = message
        super().__init__(self.message)


# ---------------------------------------------------------------------------
# XML schema loading (kept for conversion to JSON-schema; removed in S03)
# ---------------------------------------------------------------------------


def _process_dynamic_content(content: str) -> str:
    if "{{DYNAMIC_SKILLS_DESCRIPTION}}" in content:
        try:
            from strix.skills import generate_skills_description

            skills_description = generate_skills_description()
            content = content.replace("{{DYNAMIC_SKILLS_DESCRIPTION}}", skills_description)
        except ImportError:
            logger.warning("Could not import skills utilities for dynamic schema generation")
            content = content.replace(
                "{{DYNAMIC_SKILLS_DESCRIPTION}}",
                "List of skills to load for this agent (max 5). Skill discovery failed.",
            )

    return content


def _load_xml_schema(path: Path) -> dict[str, str] | None:
    """Load an XML schema file and return a dict mapping tool name → raw XML string."""
    if not path.exists():
        return None
    try:
        content = path.read_text(encoding="utf-8")

        content = _process_dynamic_content(content)

        start_tag = '<tool name="'
        end_tag = "</tool>"
        tools_dict: dict[str, str] = {}

        pos = 0
        while True:
            start_pos = content.find(start_tag, pos)
            if start_pos == -1:
                break

            name_start = start_pos + len(start_tag)
            name_end = content.find('"', name_start)
            if name_end == -1:
                break
            tool_name = content[name_start:name_end]

            end_pos = content.find(end_tag, name_end)
            if end_pos == -1:
                break
            end_pos += len(end_tag)

            tool_element = content[start_pos:end_pos]
            tools_dict[tool_name] = tool_element

            pos = end_pos

            if pos >= len(content):
                break
    except (IndexError, ValueError, UnicodeError) as e:
        logger.warning(f"Error loading schema file {path}: {e}")
        return None
    else:
        return tools_dict


# ---------------------------------------------------------------------------
# JSON-schema extraction
# ---------------------------------------------------------------------------

_XML_TYPE_MAP: dict[str, str] = {
    "string": "string",
    "boolean": "boolean",
    "bool": "boolean",
    "integer": "integer",
    "int": "integer",
    "number": "number",
    "float": "number",
    "array": "array",
    "object": "object",
}

_PYTHON_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


def _xml_type_to_json(xml_type: str) -> str:
    """Convert an XML schema type attribute to a JSON-schema type string."""
    return _XML_TYPE_MAP.get(xml_type.lower(), "string")


def _extract_description_text(element: DefusedET.Element | object) -> str:
    """Extract text content from a <description> sub-element."""
    if not hasattr(element, "find"):
        return ""
    desc = element.find("description")  # type: ignore[union-attr]
    if desc is not None and desc.text:
        return desc.text.strip()
    return ""


def _extract_json_schema_from_xml(tool_name: str, xml: str) -> dict[str, Any] | None:
    """Parse an XML tool definition into a JSON-schema dict.

    Returns a dict matching the OpenAI ``function`` envelope:
    ``{"name": ..., "description": ..., "parameters": {"type": "object", "properties": {...}, "required": [...]}}``
    or *None* if the XML cannot be parsed.
    """
    # Wrap in a root so defusedxml is happy even if there's no <tools> wrapper
    wrapped = f"<_root>{xml}</_root>"
    try:
        root = DefusedET.fromstring(wrapped)
    except DefusedET.ParseError:
        return None

    tool_el = None
    for candidate in root.findall("tool"):
        if candidate.attrib.get("name") == tool_name:
            tool_el = candidate
            break
    if tool_el is None:
        # If the XML fragment is a single <tool>, the wrapper makes it direct child
        for candidate in root:
            if hasattr(candidate, "attrib") and candidate.attrib.get("name") == tool_name:
                tool_el = candidate
                break
    if tool_el is None:
        return None

    description = ""
    desc_el = tool_el.find("description")
    if desc_el is not None and desc_el.text:
        description = desc_el.text.strip()

    params_el = tool_el.find("parameters")
    properties: dict[str, Any] = {}
    required: list[str] = []

    if params_el is not None:
        for param in params_el.findall("parameter"):
            pname = param.attrib.get("name")
            if not pname:
                continue

            ptype = _xml_type_to_json(param.attrib.get("type", "string"))
            pdesc = _extract_description_text(param)
            prop: dict[str, Any] = {"type": ptype}
            if pdesc:
                prop["description"] = pdesc
            properties[pname] = prop

            if param.attrib.get("required", "false").lower() == "true":
                required.append(pname)

    return {
        "name": tool_name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            **({"required": required} if required else {}),
        },
    }


def _python_type_to_json(annotation: Any) -> str:
    """Map a Python type annotation to a JSON-schema type string."""
    if annotation is inspect.Parameter.empty:
        return "string"

    # Handle `X | None` (Python 3.10+) and `Optional[X]`
    origin = getattr(annotation, "__origin__", None)
    if origin is str:
        return "string"

    # Check for Union types (Optional[X] is Union[X, None])
    if origin is not None:
        import typing

        if hasattr(typing, "get_args") and hasattr(typing, "Union"):
            args = getattr(annotation, "__args__", ())
            # Filter out NoneType
            non_none = [a for a in args if a is not type(None)]
            if non_none:
                return _python_type_to_json(non_none[0])
        # list[X] → array
        if origin in (list,):
            return "array"
        # dict[X, Y] → object
        if origin in (dict,):
            return "object"

    direct = _PYTHON_TYPE_MAP.get(annotation)
    if direct:
        return direct

    return "string"


def _infer_json_schema_from_signature(func: Callable[..., Any]) -> dict[str, Any]:
    """Build a JSON-schema definition from the function's signature and docstring."""
    name = func.__name__
    doc = (func.__doc__ or "").strip()
    # Take only the first paragraph as description
    description = doc.split("\n\n")[0].strip() if doc else ""

    sig = signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    # Try to resolve type hints (may fail in edge cases)
    try:
        hints = get_type_hints(func)
    except Exception:
        hints = {}

    for pname, param in sig.parameters.items():
        if pname in ("self", "cls", "agent_state"):
            continue

        annotation = hints.get(pname, param.annotation)
        ptype = _python_type_to_json(annotation)
        prop: dict[str, Any] = {"type": ptype}

        # Extract per-parameter description from docstring (Google / Sphinx style)
        if doc:
            for line in doc.split("\n"):
                stripped = line.strip()
                if stripped.startswith(f"{pname}:") or stripped.startswith(f"{pname} -"):
                    prop["description"] = stripped.split(":", 1)[-1].split("-", 1)[-1].strip()
                    break

        properties[pname] = prop

        if param.default is inspect.Parameter.empty:
            required.append(pname)

    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            **({"required": required} if required else {}),
        },
    }


def _extract_json_schema(func: Callable[..., Any], xml_tools: dict[str, str] | None) -> dict[str, Any]:
    """Produce a JSON-schema tool definition for *func*.

    Priority:
    1. If an XML schema is available, parse it into JSON-schema.
    2. Otherwise, infer from the function signature and docstring.
    """
    name = func.__name__

    if xml_tools and name in xml_tools:
        schema = _extract_json_schema_from_xml(name, xml_tools[name])
        if schema is not None:
            return schema

    return _infer_json_schema_from_signature(func)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_module_name(func: Callable[..., Any]) -> str:
    module = inspect.getmodule(func)
    if not module:
        return "unknown"

    module_name = module.__name__
    if ".tools." in module_name:
        parts = module_name.split(".tools.")[-1].split(".")
        if len(parts) >= 1:
            return parts[0]
    return "unknown"


def _get_schema_path(func: Callable[..., Any]) -> Path | None:
    module = inspect.getmodule(func)
    if not module or not module.__name__:
        return None

    module_name = module.__name__

    if ".tools." not in module_name:
        return None

    parts = module_name.split(".tools.")[-1].split(".")
    if len(parts) < 2:
        return None

    folder = parts[0]
    file_stem = parts[1]
    schema_file = f"{file_stem}_schema.xml"

    return get_strix_resource_path("tools", folder, schema_file)


def _is_sandbox_mode() -> bool:
    return os.getenv("STRIX_SANDBOX_MODE", "false").lower() == "true"


def _is_browser_disabled() -> bool:
    if os.getenv("STRIX_DISABLE_BROWSER", "").lower() == "true":
        return True

    from strix.config import Config

    val: str = Config.load().get("env", {}).get("STRIX_DISABLE_BROWSER", "")
    return str(val).lower() == "true"


def _has_perplexity_api() -> bool:
    if os.getenv("PERPLEXITY_API_KEY"):
        return True

    from strix.config import Config

    return bool(Config.load().get("env", {}).get("PERPLEXITY_API_KEY"))


def _should_register_tool(
    *,
    sandbox_execution: bool,
    requires_browser_mode: bool,
    requires_web_search_mode: bool,
) -> bool:
    sandbox_mode = _is_sandbox_mode()

    if sandbox_mode and not sandbox_execution:
        return False
    if requires_browser_mode and _is_browser_disabled():
        return False
    return not (requires_web_search_mode and not _has_perplexity_api())


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------


def register_tool(
    func: Callable[..., Any] | None = None,
    *,
    sandbox_execution: bool = True,
    requires_browser_mode: bool = False,
    requires_web_search_mode: bool = False,
) -> Callable[..., Any]:
    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        if not _should_register_tool(
            sandbox_execution=sandbox_execution,
            requires_browser_mode=requires_browser_mode,
            requires_web_search_mode=requires_web_search_mode,
        ):
            return f

        sandbox_mode = _is_sandbox_mode()
        func_dict: dict[str, Any] = {
            "name": f.__name__,
            "function": f,
            "module": _get_module_name(f),
            "sandbox_execution": sandbox_execution,
        }

        xml_tools: dict[str, str] | None = None
        if not sandbox_mode:
            try:
                schema_path = _get_schema_path(f)
                xml_tools = _load_xml_schema(schema_path) if schema_path else None

                if xml_tools is not None and f.__name__ in xml_tools:
                    func_dict["xml_schema"] = xml_tools[f.__name__]
                else:
                    func_dict["xml_schema"] = (
                        f'<tool name="{f.__name__}">'
                        "<description>Schema not found for tool.</description>"
                        "</tool>"
                    )
            except (TypeError, FileNotFoundError) as e:
                logger.warning(f"Error loading schema for {f.__name__}: {e}")
                func_dict["xml_schema"] = (
                    f'<tool name="{f.__name__}">'
                    "<description>Error loading schema.</description>"
                    "</tool>"
                )

        # --- JSON-schema extraction (new) ---
        json_schema = _extract_json_schema(f, xml_tools)
        func_dict["json_schema"] = json_schema

        # Populate _tool_param_schemas with JSON-schema-based info
        params_info: dict[str, Any] = {
            "properties": json_schema.get("parameters", {}).get("properties", {}),
            "required": json_schema.get("parameters", {}).get("required", []),
            "has_params": bool(json_schema.get("parameters", {}).get("properties")),
        }
        _tool_param_schemas[str(func_dict["name"])] = params_info

        tools.append(func_dict)
        _tools_by_name[str(func_dict["name"])] = f

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return f(*args, **kwargs)

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


# ---------------------------------------------------------------------------
# Public query helpers
# ---------------------------------------------------------------------------


def get_tool_by_name(name: str) -> Callable[..., Any] | None:
    return _tools_by_name.get(name)


def get_tool_names() -> list[str]:
    return list(_tools_by_name.keys())


def get_tool_param_schema(name: str) -> dict[str, Any] | None:
    """Return JSON-schema-based parameter info for a registered tool.

    Returns a dict with keys ``properties``, ``required``, ``has_params``,
    or *None* if the tool is not found.
    """
    return _tool_param_schemas.get(name)


def needs_agent_state(tool_name: str) -> bool:
    tool_func = get_tool_by_name(tool_name)
    if not tool_func:
        return False
    sig = signature(tool_func)
    return "agent_state" in sig.parameters


def should_execute_in_sandbox(tool_name: str) -> bool:
    for tool in tools:
        if tool.get("name") == tool_name:
            return bool(tool.get("sandbox_execution", True))
    return True


def get_tools_definitions() -> list[dict[str, Any]]:
    """Return tool definitions in OpenAI function-calling format.

    Each entry is ``{"type": "function", "function": {...}}`` where the
    ``function`` value contains ``name``, ``description``, and ``parameters``
    conforming to JSON-schema.
    """
    definitions: list[dict[str, Any]] = []
    for tool in tools:
        json_schema = tool.get("json_schema")
        if json_schema is None:
            continue
        definitions.append({
            "type": "function",
            "function": json_schema,
        })
    return definitions


def get_tools_prompt() -> str:
    """Return an empty string. Kept for backward compatibility; removed in S03."""
    return ""


def clear_registry() -> None:
    tools.clear()
    _tools_by_name.clear()
    _tool_param_schemas.clear()

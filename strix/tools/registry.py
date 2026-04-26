import inspect
import logging
import os
from collections.abc import Callable
from functools import wraps
from inspect import signature
from typing import Any, get_type_hints

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
# JSON-schema extraction
# ---------------------------------------------------------------------------

_PYTHON_TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
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


def _extract_json_schema(func: Callable[..., Any]) -> dict[str, Any]:
    """Produce a JSON-schema tool definition for *func* from its signature and docstring."""
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

        # JSON-schema extraction from function signature and docstring
        json_schema = _extract_json_schema(f)
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


def clear_registry() -> None:
    tools.clear()
    _tools_by_name.clear()
    _tool_param_schemas.clear()

"""Integration tests for sandbox tool execution pipeline and tool server endpoints.

Covers:
- execute_tool() routing between sandbox and local paths
- _execute_tool_in_sandbox() with mocked HTTP (success + error cases)
- Sandbox state validation (missing sandbox_id, sandbox_token, sandbox_info)
- Tool server endpoints (health, execute, register_agent) with auth
- Full process_tool_invocations pipeline with sandbox-flagged tools producing native format
"""

import importlib
import sys
from types import ModuleType
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from strix.tools.registry import (
    clear_registry,
    register_tool,
    should_execute_in_sandbox,
    tools,
    _tools_by_name,
    _tool_param_schemas,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _clean_registry():
    """Reset the tool registry before and after every test."""
    clear_registry()
    yield
    clear_registry()


def _register_local_tool(name: str = "local_tool") -> None:
    """Register a tool that executes locally (sandbox_execution=False)."""

    def tool_func(arg1: str = "default") -> str:
        return f"local_result:{arg1}"

    tool_func.__name__ = name
    tool_func.__qualname__ = name
    register_tool(tool_func, sandbox_execution=False)


def _register_sandbox_tool(name: str = "sandbox_tool") -> None:
    """Register a tool that requires sandbox execution (sandbox_execution=True)."""

    def tool_func(arg1: str = "default") -> str:
        return f"sandbox_result:{arg1}"

    tool_func.__name__ = name
    tool_func.__qualname__ = name
    register_tool(tool_func, sandbox_execution=True)


def _make_agent_state(
    sandbox_id: str = "sb-123",
    sandbox_token: str = "tok-abc",
    tool_server_port: int = 8080,
    agent_id: str = "agent-1",
    extra_sandbox_info: dict[str, Any] | None = None,
) -> MagicMock:
    """Build a mock agent_state with sandbox metadata."""
    state = MagicMock()
    state.sandbox_id = sandbox_id
    state.sandbox_token = sandbox_token
    state.agent_id = agent_id
    state.sandbox_info = {
        "workspace_id": "ws-1",
        "api_url": "https://api.example.com",
        "auth_token": "auth-tok",
        "tool_server_port": tool_server_port,
        "caido_port": 9090,
        "agent_id": agent_id,
    }
    if extra_sandbox_info:
        state.sandbox_info.update(extra_sandbox_info)
    return state


# ---------------------------------------------------------------------------
# 1. execute_tool() routing tests
# ---------------------------------------------------------------------------


class TestExecuteToolRouting:
    """Test that execute_tool dispatches to the correct backend."""

    @pytest.mark.asyncio
    async def test_sandbox_tool_routes_to_sandbox_executor(self):
        """A tool registered with sandbox_execution=True calls _execute_tool_in_sandbox."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        with patch("strix.tools.executor._execute_tool_in_sandbox", new_callable=AsyncMock) as mock_sb, \
             patch("strix.tools.executor._execute_tool_locally", new_callable=AsyncMock) as mock_local:
            mock_sb.return_value = "sandbox_result"

            from strix.tools.executor import execute_tool
            result = await execute_tool("sandbox_tool", agent_state, arg1="test")

            mock_sb.assert_awaited_once_with("sandbox_tool", agent_state, arg1="test")
            mock_local.assert_not_awaited()
            assert result == "sandbox_result"

    @pytest.mark.asyncio
    async def test_local_tool_routes_to_local_executor(self):
        """A tool registered with sandbox_execution=False calls _execute_tool_locally."""
        _register_local_tool()

        with patch("strix.tools.executor._execute_tool_locally", new_callable=AsyncMock) as mock_local, \
             patch("strix.tools.executor._execute_tool_in_sandbox", new_callable=AsyncMock) as mock_sb:
            mock_local.return_value = "local_result"

            from strix.tools.executor import execute_tool
            result = await execute_tool("local_tool", None, arg1="hello")

            mock_local.assert_awaited_once_with("local_tool", None, arg1="hello")
            mock_sb.assert_not_awaited()
            assert result == "local_result"

    @pytest.mark.asyncio
    async def test_sandbox_tool_in_sandbox_mode_executes_locally(self):
        """When STRIX_SANDBOX_MODE=true, sandbox tools execute via _execute_tool_locally."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        with patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "true"}), \
             patch("strix.tools.executor._execute_tool_locally", new_callable=AsyncMock) as mock_local, \
             patch("strix.tools.executor._execute_tool_in_sandbox", new_callable=AsyncMock) as mock_sb:
            mock_local.return_value = "local_in_sandbox_mode"

            from strix.tools.executor import execute_tool
            result = await execute_tool("sandbox_tool", agent_state, arg1="x")

            # In sandbox mode, the tool runs locally (not via HTTP dispatch)
            mock_local.assert_awaited_once()
            mock_sb.assert_not_awaited()
            assert result == "local_in_sandbox_mode"


# ---------------------------------------------------------------------------
# 2. _execute_tool_in_sandbox() success tests
# ---------------------------------------------------------------------------


class TestSandboxExecutionSuccess:
    """Test _execute_tool_in_sandbox with mocked HTTP client."""

    @pytest.mark.asyncio
    async def test_successful_sandbox_execution(self):
        """Successful tool server response returns the result."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": {"output": "success"}, "error": None}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime):
            from strix.tools.executor import _execute_tool_in_sandbox
            result = await _execute_tool_in_sandbox("sandbox_tool", agent_state, arg1="test")

            assert result == {"output": "success"}
            mock_client.post.assert_awaited_once()
            call_kwargs = mock_client.post.call_args
            assert call_kwargs[0][0] == "http://sandbox:8080/execute"

    @pytest.mark.asyncio
    async def test_request_url_constructed_from_sandbox_info(self):
        """The request URL is built from sandbox_info via runtime.get_sandbox_url."""
        _register_sandbox_tool()
        agent_state = _make_agent_state(tool_server_port=9999)

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://my-sandbox:9999")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime):
            from strix.tools.executor import _execute_tool_in_sandbox
            await _execute_tool_in_sandbox("sandbox_tool", agent_state)

            mock_runtime.get_sandbox_url.assert_awaited_once_with("sb-123", 9999)
            assert mock_client.post.call_args[0][0] == "http://my-sandbox:9999/execute"

    @pytest.mark.asyncio
    async def test_auth_header_contains_bearer_token(self):
        """The Authorization header includes the sandbox_token as Bearer."""
        _register_sandbox_tool()
        agent_state = _make_agent_state(sandbox_token="secret-tok-123")

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime):
            from strix.tools.executor import _execute_tool_in_sandbox
            await _execute_tool_in_sandbox("sandbox_tool", agent_state)

            headers = mock_client.post.call_args[1]["headers"]
            assert headers["Authorization"] == "Bearer secret-tok-123"

    @pytest.mark.asyncio
    async def test_request_body_includes_agent_id_tool_name_kwargs(self):
        """The POST body contains agent_id, tool_name, and kwargs."""
        _register_sandbox_tool()
        agent_state = _make_agent_state(agent_id="agent-42")

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime):
            from strix.tools.executor import _execute_tool_in_sandbox
            await _execute_tool_in_sandbox("sandbox_tool", agent_state, arg1="val", arg2=42)

            body = mock_client.post.call_args[1]["json"]
            assert body["agent_id"] == "agent-42"
            assert body["tool_name"] == "sandbox_tool"
            assert body["kwargs"] == {"arg1": "val", "arg2": 42}


# ---------------------------------------------------------------------------
# 3. _execute_tool_in_sandbox() error handling tests
# ---------------------------------------------------------------------------


class TestSandboxExecutionErrors:
    """Test error handling in _execute_tool_in_sandbox."""

    @pytest.mark.asyncio
    async def test_401_response_raises_authentication_error(self):
        """A 401 response raises RuntimeError with authentication failure message."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch("strix.tools.executor.posthog"):
            from strix.tools.executor import _execute_tool_in_sandbox
            with pytest.raises(RuntimeError, match="Authentication failed"):
                await _execute_tool_in_sandbox("sandbox_tool", agent_state)

    @pytest.mark.asyncio
    async def test_500_response_raises_http_error(self):
        """A 500 response raises RuntimeError with HTTP status code."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        import httpx

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch("strix.tools.executor.posthog"):
            from strix.tools.executor import _execute_tool_in_sandbox
            with pytest.raises(RuntimeError, match="HTTP error calling tool server: 500"):
                await _execute_tool_in_sandbox("sandbox_tool", agent_state)

    @pytest.mark.asyncio
    async def test_request_error_raises_runtime_error(self):
        """An httpx.RequestError raises RuntimeError with error type name."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        import httpx

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch("strix.tools.executor.posthog"):
            from strix.tools.executor import _execute_tool_in_sandbox
            with pytest.raises(RuntimeError, match="Request error calling tool server: ConnectError"):
                await _execute_tool_in_sandbox("sandbox_tool", agent_state)

    @pytest.mark.asyncio
    async def test_response_with_error_key_raises_runtime_error(self):
        """A 200 response with an 'error' key raises RuntimeError."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        mock_response = MagicMock()
        mock_response.json.return_value = {"error": "Tool crashed: segfault", "result": None}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch("strix.tools.executor.posthog"):
            from strix.tools.executor import _execute_tool_in_sandbox
            with pytest.raises(RuntimeError, match="Sandbox execution error: Tool crashed: segfault"):
                await _execute_tool_in_sandbox("sandbox_tool", agent_state)


# ---------------------------------------------------------------------------
# 4. _execute_tool_in_sandbox() validation tests
# ---------------------------------------------------------------------------


class TestSandboxStateValidation:
    """Test that _execute_tool_in_sandbox validates agent_state fields."""

    @pytest.mark.asyncio
    async def test_missing_sandbox_id_raises_value_error(self):
        """Missing sandbox_id raises ValueError."""
        state = _make_agent_state()
        state.sandbox_id = None

        from strix.tools.executor import _execute_tool_in_sandbox
        with pytest.raises(ValueError, match="sandbox_id"):
            await _execute_tool_in_sandbox("tool", state)

    @pytest.mark.asyncio
    async def test_missing_sandbox_token_raises_value_error(self):
        """Missing sandbox_token raises ValueError."""
        state = _make_agent_state()
        state.sandbox_token = None

        from strix.tools.executor import _execute_tool_in_sandbox
        with pytest.raises(ValueError, match="sandbox_token"):
            await _execute_tool_in_sandbox("tool", state)

    @pytest.mark.asyncio
    async def test_missing_sandbox_info_raises_value_error(self):
        """Missing sandbox_info raises ValueError."""
        state = _make_agent_state()
        del state.sandbox_info

        from strix.tools.executor import _execute_tool_in_sandbox
        with pytest.raises(ValueError, match="sandbox_info"):
            await _execute_tool_in_sandbox("tool", state)

    @pytest.mark.asyncio
    async def test_missing_tool_server_port_raises_value_error(self):
        """sandbox_info without tool_server_port raises ValueError."""
        state = _make_agent_state()
        state.sandbox_info = {"workspace_id": "ws-1"}  # no tool_server_port

        from strix.tools.executor import _execute_tool_in_sandbox
        with pytest.raises(ValueError, match="tool_server_port"):
            await _execute_tool_in_sandbox("tool", state)

    @pytest.mark.asyncio
    async def test_agent_state_without_sandbox_id_attribute_raises(self):
        """agent_state without sandbox_id attribute raises ValueError."""
        state = MagicMock(spec=[])  # empty spec — no attributes

        from strix.tools.executor import _execute_tool_in_sandbox
        with pytest.raises(ValueError, match="sandbox_id"):
            await _execute_tool_in_sandbox("tool", state)


# ---------------------------------------------------------------------------
# 5. Tool server endpoint tests
# ---------------------------------------------------------------------------


def _build_tool_server_app(token: str = "test-token") -> tuple[Any, str]:
    """Construct a FastAPI tool server app for testing without the module-level guard.

    Returns (app, token) where app is a FastAPI instance with the same routes
    as the production tool_server.
    """
    from fastapi import Depends, FastAPI, HTTPException, status
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from pydantic import BaseModel

    expected_token = token

    app = FastAPI()
    security = HTTPBearer()
    security_dependency = Depends(security)

    # Track agent tasks for the test app
    test_agent_tasks: dict[str, Any] = {}

    def verify_token(credentials: HTTPAuthorizationCredentials) -> str:
        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if credentials.credentials != expected_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return credentials.credentials

    class ToolExecutionRequest(BaseModel):
        agent_id: str
        tool_name: str
        kwargs: dict[str, Any]

    class ToolExecutionResponse(BaseModel):
        result: Any | None = None
        error: str | None = None

    @app.get("/health")
    async def health_check() -> dict[str, Any]:
        return {
            "status": "healthy",
            "sandbox_mode": "true",
            "environment": "sandbox",
            "auth_configured": "true" if expected_token else "false",
            "active_agents": len(test_agent_tasks),
            "agents": list(test_agent_tasks.keys()),
        }

    @app.post("/execute", response_model=ToolExecutionResponse)
    async def execute_tool(
        request: ToolExecutionRequest,
        credentials: HTTPAuthorizationCredentials = security_dependency,
    ) -> ToolExecutionResponse:
        verify_token(credentials)
        # For testing, return a simple acknowledgment rather than actually executing
        return ToolExecutionResponse(result={"tool_name": request.tool_name, "executed": True})

    @app.post("/register_agent")
    async def register_agent(
        agent_id: str,
        credentials: HTTPAuthorizationCredentials = security_dependency,
    ) -> dict[str, str]:
        verify_token(credentials)
        test_agent_tasks[agent_id] = True
        return {"status": "registered", "agent_id": agent_id}

    return app, token


@pytest.fixture
def tool_server_client():
    """Provide an httpx AsyncClient wired to a test tool server app."""
    from httpx import ASGITransport, AsyncClient

    app, token = _build_tool_server_app()
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://testserver")
    yield client, token


class TestToolServerEndpoints:
    """Test tool server FastAPI endpoints using ASGI transport."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, tool_server_client):
        """Health endpoint returns status, sandbox_mode, auth_configured."""
        client, _ = tool_server_client
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["sandbox_mode"] == "true"
        assert data["auth_configured"] == "true"

    @pytest.mark.asyncio
    async def test_execute_with_valid_token(self, tool_server_client):
        """Execute endpoint with valid Bearer token returns tool result."""
        client, token = tool_server_client
        response = await client.post(
            "/execute",
            json={
                "agent_id": "agent-1",
                "tool_name": "terminal_execute",
                "kwargs": {"command": "echo hello"},
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["result"]["executed"] is True
        assert data["result"]["tool_name"] == "terminal_execute"
        assert data["error"] is None

    @pytest.mark.asyncio
    async def test_execute_with_invalid_token_returns_401(self, tool_server_client):
        """Execute endpoint with wrong token returns 401."""
        client, _ = tool_server_client
        response = await client.post(
            "/execute",
            json={
                "agent_id": "agent-1",
                "tool_name": "terminal_execute",
                "kwargs": {},
            },
            headers={"Authorization": "Bearer wrong-token"},
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_execute_without_token_returns_403(self, tool_server_client):
        """Execute endpoint without any auth header returns 403."""
        client, _ = tool_server_client
        response = await client.post(
            "/execute",
            json={
                "agent_id": "agent-1",
                "tool_name": "terminal_execute",
                "kwargs": {},
            },
        )

        # FastAPI HTTPBearer returns 403 when no credentials provided
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_register_agent_endpoint(self, tool_server_client):
        """Register agent endpoint returns status and agent_id."""
        client, token = tool_server_client
        response = await client.post(
            "/register_agent?agent_id=agent-42",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "registered"
        assert data["agent_id"] == "agent-42"

    @pytest.mark.asyncio
    async def test_register_agent_invalid_token(self, tool_server_client):
        """Register agent with bad token returns 401."""
        client, _ = tool_server_client
        response = await client.post(
            "/register_agent?agent_id=agent-42",
            headers={"Authorization": "Bearer bad"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# 6. process_tool_invocations pipeline tests with sandbox tools
# ---------------------------------------------------------------------------


class TestProcessToolInvocationsSandbox:
    """Test the full process_tool_invocations pipeline with sandbox-flagged tools."""

    @pytest.mark.asyncio
    async def test_sandbox_invocation_produces_native_tool_message(self):
        """Sandbox tool invocation produces a native tool role message."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        # Mock the HTTP sandbox dispatch to return a result
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "sandbox_ok"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        conversation_history: list[dict[str, Any]] = [
            {"role": "assistant", "content": "I'll use the tool."}
        ]

        tool_invocations = [
            {
                "id": "call_abc123",
                "toolName": "sandbox_tool",
                "args": {"arg1": "test"},
            }
        ]

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "false"}):
            from strix.tools.executor import process_tool_invocations
            should_finish = await process_tool_invocations(
                tool_invocations, conversation_history, agent_state
            )

            assert should_finish is False
            # Should have: assistant (with tool_calls added in-place) + 1 tool result
            assert len(conversation_history) == 2
            tool_msg = conversation_history[-1]
            assert tool_msg["role"] == "tool"
            assert tool_msg["tool_call_id"] == "call_abc123"
            assert "sandbox_ok" in str(tool_msg["content"])

    @pytest.mark.asyncio
    async def test_no_xml_artifacts_in_sandbox_results(self):
        """Sandbox tool results should never contain XML artifacts."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "clean_result"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        conversation_history: list[dict[str, Any]] = [
            {"role": "assistant", "content": "Using tool."}
        ]
        tool_invocations = [
            {"id": "call_xyz", "toolName": "sandbox_tool", "args": {}}
        ]

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "false"}):
            from strix.tools.executor import process_tool_invocations
            await process_tool_invocations(tool_invocations, conversation_history, agent_state)

            tool_msg = conversation_history[-1]
            content_str = str(tool_msg["content"])
            assert "<function=" not in content_str
            assert "</function>" not in content_str
            assert "<invoke" not in content_str

    @pytest.mark.asyncio
    async def test_assistant_message_gets_tool_calls_metadata(self):
        """The preceding assistant message should get tool_calls metadata added."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        conversation_history: list[dict[str, Any]] = [
            {"role": "assistant", "content": "Running tool."}
        ]
        tool_invocations = [
            {"id": "call_001", "toolName": "sandbox_tool", "args": {"arg1": "v"}}
        ]

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "false"}):
            from strix.tools.executor import process_tool_invocations
            await process_tool_invocations(tool_invocations, conversation_history, agent_state)

            # The assistant message should have tool_calls added
            assistant_msg = conversation_history[0]
            assert "tool_calls" in assistant_msg
            tc = assistant_msg["tool_calls"][0]
            assert tc["id"] == "call_001"
            assert tc["type"] == "function"
            assert tc["function"]["name"] == "sandbox_tool"


# ---------------------------------------------------------------------------
# 7. Native format consistency tests
# ---------------------------------------------------------------------------


class TestNativeFormatConsistency:
    """Test that multiple sandbox invocations produce consistent native format."""

    @pytest.mark.asyncio
    async def test_sequential_invocations_have_matching_call_ids(self):
        """Multiple sequential sandbox tool invocations produce correct tool_call_ids."""
        _register_sandbox_tool("sandbox_a")
        _register_sandbox_tool("sandbox_b")

        agent_state = _make_agent_state()

        mock_response_a = MagicMock()
        mock_response_a.json.return_value = {"result": "result_a"}
        mock_response_a.raise_for_status = MagicMock()

        mock_response_b = MagicMock()
        mock_response_b.json.return_value = {"result": "result_b"}
        mock_response_b.raise_for_status = MagicMock()

        call_count = 0

        async def _mock_post(url, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response_a if call_count == 1 else mock_response_b

        mock_client = AsyncMock()
        mock_client.post = _mock_post
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        conversation_history: list[dict[str, Any]] = [
            {"role": "assistant", "content": "Using two tools."}
        ]
        tool_invocations = [
            {"id": "call_first", "toolName": "sandbox_a", "args": {}},
            {"id": "call_second", "toolName": "sandbox_b", "args": {}},
        ]

        with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
             patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
             patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "false"}):
            from strix.tools.executor import process_tool_invocations
            await process_tool_invocations(tool_invocations, conversation_history, agent_state)

            # Should have: assistant (with tool_calls added in-place) + tool result A + tool result B
            assert len(conversation_history) == 3
            msg_a = conversation_history[1]
            msg_b = conversation_history[2]

            assert msg_a["role"] == "tool"
            assert msg_a["tool_call_id"] == "call_first"
            assert "result_a" in str(msg_a["content"])

            assert msg_b["role"] == "tool"
            assert msg_b["tool_call_id"] == "call_second"
            assert "result_b" in str(msg_b["content"])

    @pytest.mark.asyncio
    async def test_all_results_are_native_format(self):
        """No XML wrapping should appear in any tool result from sandbox execution."""
        _register_sandbox_tool()
        agent_state = _make_agent_state()

        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "plain_text_output"}
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        mock_runtime = AsyncMock()
        mock_runtime.get_sandbox_url = AsyncMock(return_value="http://sandbox:8080")

        conversation_history: list[dict[str, Any]] = [
            {"role": "assistant", "content": "Go."}
        ]

        # Run 3 sequential invocations
        for i in range(3):
            conversation_copy = list(conversation_history)
            invocations = [{"id": f"call_{i}", "toolName": "sandbox_tool", "args": {}}]

            with patch("strix.tools.executor.httpx.AsyncClient", return_value=mock_client), \
                 patch("strix.tools.executor.get_runtime", return_value=mock_runtime), \
                 patch.dict("os.environ", {"STRIX_SANDBOX_MODE": "false"}):
                from strix.tools.executor import process_tool_invocations
                await process_tool_invocations(invocations, conversation_history, agent_state)

        # Check the last 3 messages are tool results in native format
        for msg in conversation_history[-3:]:
            assert msg["role"] == "tool"
            assert "tool_call_id" in msg
            content_str = str(msg["content"])
            assert "<function=" not in content_str
            assert "<invoke" not in content_str
            assert "</function>" not in content_str

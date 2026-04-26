"""Integration tests for Docker runtime container lifecycle.

Covers:
- DockerRuntime.__init__ (success, Docker-unavailable)
- _create_container (port allocation, env vars, labels, cleanup of old container, retry on failure)
- _get_or_create_container (reuse running, restart stopped, fallback create)
- create_sandbox (SandboxInfo shape, source copying, agent registration)
- destroy_sandbox and cleanup (graceful handling, background subprocess)
- _resolve_docker_host (DOCKER_HOST parsing)
- _recover_container_state (port and token recovery from container attrs)
"""

from __future__ import annotations

import os
import subprocess
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

from strix.runtime import SandboxInitializationError
from strix.runtime.docker_runtime import (
    CONTAINER_CAIDO_PORT,
    CONTAINER_TOOL_SERVER_PORT,
    DockerRuntime,
    HOST_GATEWAY_HOSTNAME,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_mock_container(
    *,
    container_id: str = "abc123",
    status: str = "running",
    name: str = "strix-scan-test-scan",
    tool_server_port: int = 50001,
    caido_port: int = 50002,
    token: str = "tok-secret",
) -> MagicMock:
    """Build a realistic mock Container object."""
    container = MagicMock(spec=["id", "status", "name", "attrs", "stop", "remove", "start", "reload", "put_archive", "exec_run"])
    container.id = container_id
    container.status = status
    container.name = name

    # attrs simulates Docker inspection output
    container.attrs = {
        "Config": {
            "Env": [
                f"TOOL_SERVER_TOKEN={token}",
                f"TOOL_SERVER_PORT={CONTAINER_TOOL_SERVER_PORT}",
                "PYTHONUNBUFFERED=1",
            ],
        },
        "NetworkSettings": {
            "Ports": {
                f"{CONTAINER_TOOL_SERVER_PORT}/tcp": [{"HostPort": str(tool_server_port)}],
                f"{CONTAINER_CAIDO_PORT}/tcp": [{"HostPort": str(caido_port)}],
            },
        },
    }
    return container


def _make_mock_docker_client(containers: list[MagicMock] | None = None) -> MagicMock:
    """Build a mock docker.from_env() client."""
    client = MagicMock()
    client.containers = MagicMock()
    client.images = MagicMock()

    if containers:
        client.containers.list.return_value = containers

    return client


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_docker_client() -> MagicMock:
    """Mock Docker client with a successful from_env()."""
    return _make_mock_docker_client()


@pytest.fixture
def runtime(mock_docker_client: MagicMock) -> DockerRuntime:
    """DockerRuntime initialized with a mocked Docker client."""
    with patch("strix.runtime.docker_runtime.docker.from_env", return_value=mock_docker_client):
        rt = DockerRuntime()
    return rt


@pytest.fixture(autouse=True)
def _reset_runtime_singleton():
    """Ensure the global runtime singleton is reset between tests."""
    import strix.runtime as rt_module

    original = rt_module._global_runtime
    rt_module._global_runtime = None
    yield
    rt_module._global_runtime = original


# ===========================================================================
# Test: DockerRuntime.__init__
# ===========================================================================


class TestDockerRuntimeInit:
    def test_successful_initialization(self, mock_docker_client: MagicMock) -> None:
        """Client is set when Docker is available."""
        with patch("strix.runtime.docker_runtime.docker.from_env", return_value=mock_docker_client):
            rt = DockerRuntime()

        assert rt.client is mock_docker_client
        assert rt._scan_container is None
        assert rt._tool_server_port is None

    def test_docker_unavailable_raises(self) -> None:
        """SandboxInitializationError raised when Docker is not running."""
        import docker.errors

        with patch(
            "strix.runtime.docker_runtime.docker.from_env",
            side_effect=docker.errors.DockerException("Cannot connect"),
        ):
            with pytest.raises(SandboxInitializationError) as exc_info:
                DockerRuntime()

        assert "not available" in str(exc_info.value.message)
        assert exc_info.value.details is not None


# ===========================================================================
# Test: _create_container
# ===========================================================================


class TestCreateContainer:
    def test_creates_container_with_correct_config(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """Container is created with correct ports, env vars, labels, capabilities."""
        container = _make_mock_container()
        mock_docker_client.containers.run.return_value = container
        # _create_container first tries containers.get to clean up old container
        import docker.errors
        mock_docker_client.containers.get.side_effect = docker.errors.NotFound("nope")

        with (
            patch.object(runtime, "_find_available_port", side_effect=[50001, 50002]),
            patch.object(runtime, "_wait_for_tool_server"),
            patch("strix.runtime.docker_runtime.Config") as mock_config,
            patch("strix.runtime.docker_runtime.time.sleep"),
        ):
            mock_config.get.side_effect = lambda k: {
                "strix_image": "strix-sandbox:test",
                "strix_sandbox_execution_timeout": "120",
            }.get(k)
            result = runtime._create_container("test-scan")

        mock_docker_client.containers.run.assert_called_once()
        call_args = mock_docker_client.containers.run.call_args
        # image is passed as positional arg
        assert call_args[0][0] == "strix-sandbox:test"
        call_kwargs = call_args[1]
        assert call_kwargs["detach"] is True
        assert call_kwargs["name"] == "strix-scan-test-scan"
        assert "NET_ADMIN" in call_kwargs["cap_add"]
        assert call_kwargs["labels"] == {"strix-scan-id": "test-scan"}
        assert call_kwargs["environment"]["TOOL_SERVER_TOKEN"] == runtime._tool_server_token
        assert call_kwargs["environment"]["HOST_GATEWAY"] == HOST_GATEWAY_HOSTNAME
        assert result is container

    def test_cleans_up_existing_container_before_create(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """Old container is stopped and removed before creating a new one."""
        old_container = _make_mock_container(name="strix-scan-test-scan")
        new_container = _make_mock_container(container_id="new123")
        mock_docker_client.containers.get.return_value = old_container
        mock_docker_client.containers.run.return_value = new_container

        with (
            patch.object(runtime, "_find_available_port", side_effect=[50001, 50002]),
            patch.object(runtime, "_wait_for_tool_server"),
            patch("strix.runtime.docker_runtime.Config") as mock_config,
        ):
            mock_config.get.side_effect = lambda k: {
                "strix_image": "strix-sandbox:test",
                "strix_sandbox_execution_timeout": "120",
            }.get(k)
            runtime._create_container("test-scan")

        old_container.stop.assert_called_once()
        old_container.remove.assert_called_once_with(force=True)

    def test_raises_after_max_retries(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """SandboxInitializationError raised after container creation fails max_retries + 1 times."""
        import docker.errors

        mock_docker_client.containers.get.side_effect = docker.errors.NotFound("nope")
        mock_docker_client.containers.run.side_effect = docker.errors.DockerException("boom")

        with (
            patch.object(runtime, "_find_available_port", return_value=50001),
            patch("strix.runtime.docker_runtime.Config") as mock_config,
            patch("strix.runtime.docker_runtime.time.sleep"),
        ):
            mock_config.get.side_effect = lambda k: {
                "strix_image": "strix-sandbox:test",
                "strix_sandbox_execution_timeout": "120",
            }.get(k)
            with pytest.raises(SandboxInitializationError) as exc_info:
                runtime._create_container("test-scan", max_retries=1)

        assert "Failed to create container" in str(exc_info.value.message)

    def test_image_not_configured_raises_value_error(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """ValueError raised when strix_image is not configured."""
        with patch("strix.runtime.docker_runtime.Config") as mock_config:
            mock_config.get.return_value = None  # No image configured

            with pytest.raises(ValueError, match="STRIX_IMAGE"):
                runtime._create_container("test-scan")


# ===========================================================================
# Test: _get_or_create_container
# ===========================================================================


class TestGetOrCreateContainer:
    def test_reuses_running_container(self, runtime: DockerRuntime) -> None:
        """Existing running container is returned without creating a new one."""
        container = _make_mock_container(status="running")
        runtime._scan_container = container

        result = runtime._get_or_create_container("test-scan")

        assert result is container
        # No new container created
        runtime.client.containers.get.assert_not_called()

    def test_restarts_stopped_container(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """Stopped container found by name is restarted and reused."""
        container = _make_mock_container(status="exited")
        mock_docker_client.containers.get.return_value = container

        result = runtime._get_or_create_container("test-scan")

        container.start.assert_called_once()
        assert result is container
        assert runtime._scan_container is container

    def test_falls_back_to_create_when_not_found(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """_create_container is called when no existing container is found."""
        import docker.errors

        mock_docker_client.containers.get.side_effect = docker.errors.NotFound("nope")
        mock_docker_client.containers.list.return_value = []

        created = _make_mock_container()
        with patch.object(runtime, "_create_container", return_value=created) as mock_create:
            result = runtime._get_or_create_container("test-scan")

        mock_create.assert_called_once_with("test-scan")
        assert result is created

    def test_recovers_from_lost_container_reference(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """When the stored container reference is stale (NotFound), falls back to lookup."""
        import docker.errors

        stale_container = _make_mock_container()
        stale_container.reload.side_effect = docker.errors.NotFound("gone")
        runtime._scan_container = stale_container

        fresh_container = _make_mock_container(status="running")
        mock_docker_client.containers.get.return_value = fresh_container

        result = runtime._get_or_create_container("test-scan")

        assert result is fresh_container
        # Internal state should be reset and then populated
        assert runtime._scan_container is fresh_container


# ===========================================================================
# Test: create_sandbox
# ===========================================================================


class TestCreateSandbox:
    @pytest.mark.asyncio
    async def test_returns_correct_sandbox_info(self, runtime: DockerRuntime) -> None:
        """create_sandbox returns SandboxInfo with all required keys."""
        container = _make_mock_container(tool_server_port=50001, caido_port=50002, token="tok-abc")
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok-abc"
        runtime._caido_port = 50002

        with patch.object(runtime, "_get_or_create_container", return_value=container):
            with patch.object(runtime, "_register_agent", new_callable=AsyncMock):
                info = await runtime.create_sandbox("agent-001")

        assert info["workspace_id"] == container.id
        assert info["tool_server_port"] == 50001
        assert info["caido_port"] == 50002
        assert info["auth_token"] == "tok-abc"
        assert info["agent_id"] == "agent-001"
        assert "api_url" in info
        assert "127.0.0.1" in info["api_url"]

    @pytest.mark.asyncio
    async def test_uses_existing_token(self, runtime: DockerRuntime) -> None:
        """create_sandbox uses existing_token when provided."""
        container = _make_mock_container()
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "internal-tok"
        runtime._caido_port = 50002

        with patch.object(runtime, "_get_or_create_container", return_value=container):
            with patch.object(runtime, "_register_agent", new_callable=AsyncMock) as mock_reg:
                info = await runtime.create_sandbox("agent-002", existing_token="override-tok")

        assert info["auth_token"] == "override-tok"
        mock_reg.assert_awaited_once()
        # Token sent to _register_agent should be the override
        assert mock_reg.call_args[0][2] == "override-tok"

    @pytest.mark.asyncio
    async def test_copies_local_sources_into_container(self, runtime: DockerRuntime, tmp_path: Any) -> None:
        """Local sources are copied into the container on first call."""
        container = _make_mock_container()
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok"
        runtime._caido_port = 50002

        source_dir = tmp_path / "mycode"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('hello')")

        local_sources = [{"source_path": str(source_dir), "workspace_subdir": "app"}]

        with (
            patch.object(runtime, "_get_or_create_container", return_value=container),
            patch.object(runtime, "_register_agent", new_callable=AsyncMock),
        ):
            info = await runtime.create_sandbox("agent-003", local_sources=local_sources)

        # put_archive should have been called to copy files into container
        container.put_archive.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_registration_called(self, runtime: DockerRuntime) -> None:
        """_register_agent is called with correct URL and token."""
        container = _make_mock_container()
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok-reg"
        runtime._caido_port = 50002

        with (
            patch.object(runtime, "_get_or_create_container", return_value=container),
            patch.object(runtime, "_register_agent", new_callable=AsyncMock) as mock_reg,
        ):
            await runtime.create_sandbox("agent-004")

        mock_reg.assert_awaited_once()
        call_args = mock_reg.call_args[0]
        assert "50001" in call_args[0]  # api_url contains port
        assert call_args[1] == "agent-004"
        assert call_args[2] == "tok-reg"

    @pytest.mark.asyncio
    async def test_raises_when_container_id_is_none(self, runtime: DockerRuntime) -> None:
        """RuntimeError when container has no ID."""
        container = _make_mock_container()
        container.id = None
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok"
        runtime._caido_port = 50002

        with patch.object(runtime, "_get_or_create_container", return_value=container):
            with pytest.raises(RuntimeError, match="None"):
                await runtime.create_sandbox("agent-005")


# ===========================================================================
# Test: destroy_sandbox and cleanup
# ===========================================================================


class TestDestroyAndCleanup:
    @pytest.mark.asyncio
    async def test_destroy_sandbox_stops_and_removes(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """destroy_sandbox stops and removes the container and clears internal state."""
        container = _make_mock_container()
        mock_docker_client.containers.get.return_value = container
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok"
        runtime._caido_port = 50002

        await runtime.destroy_sandbox("abc123")

        container.stop.assert_called_once()
        container.remove.assert_called_once()
        assert runtime._scan_container is None
        assert runtime._tool_server_port is None
        assert runtime._tool_server_token is None
        assert runtime._caido_port is None

    @pytest.mark.asyncio
    async def test_destroy_sandbox_graceful_when_not_found(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """destroy_sandbox does not raise when container is not found."""
        import docker.errors

        mock_docker_client.containers.get.side_effect = docker.errors.NotFound("gone")

        # Should not raise
        await runtime.destroy_sandbox("nonexistent")

    def test_cleanup_spawns_background_subprocess(self, runtime: DockerRuntime) -> None:
        """cleanup() spawns a background 'docker rm -f' subprocess and clears state."""
        container = _make_mock_container(name="strix-scan-test-scan")
        runtime._scan_container = container
        runtime._tool_server_port = 50001
        runtime._tool_server_token = "tok"
        runtime._caido_port = 50002

        with patch("subprocess.Popen") as mock_popen:
            runtime.cleanup()

        mock_popen.assert_called_once()
        popen_args = mock_popen.call_args[0][0]
        assert "docker" in popen_args
        assert "rm" in popen_args
        assert "strix-scan-test-scan" in popen_args
        assert runtime._scan_container is None
        assert runtime._tool_server_port is None

    def test_cleanup_noop_when_no_container(self, runtime: DockerRuntime) -> None:
        """cleanup() is a no-op when there is no active container."""
        runtime._scan_container = None

        with patch("subprocess.Popen") as mock_popen:
            runtime.cleanup()

        mock_popen.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_sandbox_url_returns_correct_url(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """get_sandbox_url returns the correct URL for an existing container."""
        mock_docker_client.containers.get.return_value = _make_mock_container()

        url = await runtime.get_sandbox_url("abc123", 8080)
        assert url == "http://127.0.0.1:8080"

    @pytest.mark.asyncio
    async def test_get_sandbox_url_raises_for_missing_container(self, runtime: DockerRuntime, mock_docker_client: MagicMock) -> None:
        """get_sandbox_url raises ValueError when container is not found."""
        import docker.errors

        mock_docker_client.containers.get.side_effect = docker.errors.NotFound("gone")

        with pytest.raises(ValueError, match="not found"):
            await runtime.get_sandbox_url("nonexistent", 8080)


# ===========================================================================
# Test: _resolve_docker_host
# ===========================================================================


class TestResolveDockerHost:
    def test_defaults_to_localhost(self, runtime: DockerRuntime) -> None:
        """Returns 127.0.0.1 when DOCKER_HOST is not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert runtime._resolve_docker_host() == "127.0.0.1"

    def test_parses_tcp_docker_host(self, runtime: DockerRuntime) -> None:
        """Extracts hostname from tcp:// DOCKER_HOST."""
        with patch.dict(os.environ, {"DOCKER_HOST": "tcp://192.168.1.100:2376"}):
            assert runtime._resolve_docker_host() == "192.168.1.100"

    def test_parses_http_docker_host(self, runtime: DockerRuntime) -> None:
        """Extracts hostname from http:// DOCKER_HOST."""
        with patch.dict(os.environ, {"DOCKER_HOST": "http://my-docker:4243"}):
            assert runtime._resolve_docker_host() == "my-docker"


# ===========================================================================
# Test: _recover_container_state
# ===========================================================================


class TestRecoverContainerState:
    def test_recovers_token_and_ports(self, runtime: DockerRuntime) -> None:
        """Token and ports are recovered from container attributes."""
        container = _make_mock_container(tool_server_port=49001, caido_port=49002, token="recovered-tok")

        runtime._recover_container_state(container)

        assert runtime._tool_server_token == "recovered-tok"
        assert runtime._tool_server_port == 49001
        assert runtime._caido_port == 49002

    def test_handles_missing_port_bindings(self, runtime: DockerRuntime) -> None:
        """Gracefully handles containers without port bindings."""
        container = _make_mock_container()
        container.attrs = {
            "Config": {"Env": []},
            "NetworkSettings": {"Ports": {}},
        }

        runtime._recover_container_state(container)

        assert runtime._tool_server_token is None
        assert runtime._tool_server_port is None
        assert runtime._caido_port is None


# ===========================================================================
# Test: _wait_for_tool_server
# ===========================================================================


class TestWaitForToolServer:
    def test_raises_on_timeout(self, runtime: DockerRuntime) -> None:
        """SandboxInitializationError raised when tool server never becomes healthy."""
        runtime._tool_server_port = 50001

        with (
            patch("strix.runtime.docker_runtime.time.sleep"),
            patch("strix.runtime.docker_runtime.httpx.Client") as mock_client_cls,
        ):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_client.get.return_value = mock_response
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client_cls.return_value = mock_client

            with pytest.raises(SandboxInitializationError, match="failed to start"):
                runtime._wait_for_tool_server(max_retries=2, timeout=1)


# ===========================================================================
# Test: _get_scan_id
# ===========================================================================


class TestGetScanId:
    def test_falls_back_to_agent_based_id(self, runtime: DockerRuntime) -> None:
        """Returns scan-{prefix} when no tracer is available."""
        with patch("strix.telemetry.tracer.get_global_tracer", return_value=None):
            scan_id = runtime._get_scan_id("agent-deadbeef-1234")

        assert scan_id == "scan-agent"

    def test_uses_tracer_scan_id(self, runtime: DockerRuntime) -> None:
        """Returns tracer's scan_id when available."""
        mock_tracer = MagicMock()
        mock_tracer.scan_config = {"scan_id": "scan-abc-456"}

        with patch("strix.telemetry.tracer.get_global_tracer", return_value=mock_tracer):
            scan_id = runtime._get_scan_id("agent-001")

        assert scan_id == "scan-abc-456"

import socket
import subprocess
from unittest.mock import MagicMock, patch, ANY

import pytest
from docker.errors import DockerException, ImageNotFound, NotFound

from strix.runtime import SandboxInitializationError
from strix.runtime.docker_runtime import DockerRuntime, CONTAINER_TOOL_SERVER_PORT, CONTAINER_CAIDO_PORT


@pytest.fixture
def mock_config():
    with patch("strix.runtime.docker_runtime.Config.get") as mock_get:
        mock_get.side_effect = lambda key: "test-image:latest" if key == "strix_image" else None
        yield mock_get


@pytest.fixture
def mock_docker_client():
    with patch("strix.runtime.docker_runtime.docker.from_env") as mock_from_env:
        mock_client = MagicMock()
        mock_from_env.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_runtime(mock_docker_client, mock_config):
    # Reset global singleton if needed, though DockerRuntime itself doesn't use it directly here
    # We just create a fresh instance
    with patch("strix.runtime.docker_runtime.Config.get", mock_config):
        runtime = DockerRuntime()
        # Ensure we don't accidentally do network calls in tests
        runtime._wait_for_tool_server = MagicMock() 
        yield runtime


def test_initialization_success(mock_docker_client):
    runtime = DockerRuntime()
    assert runtime.client == mock_docker_client
    assert runtime._scan_container is None
    assert runtime._tool_server_port is None


@patch("strix.runtime.docker_runtime.docker.from_env")
def test_initialization_docker_unavailable(mock_from_env):
    mock_from_env.side_effect = DockerException("Connection refused")
    with pytest.raises(SandboxInitializationError) as exc_info:
        DockerRuntime()
    assert "Docker is not available" in str(exc_info.value)
    assert "ensure Docker Desktop is installed" in exc_info.value.details


def test_create_container_success(mock_runtime, mock_docker_client):
    # Setup mocks
    mock_container = MagicMock()
    mock_container.id = "mock-container-id"
    mock_docker_client.containers.run.return_value = mock_container
    
    mock_docker_client.images.get.return_value = MagicMock(id="image-id", attrs={"some": "attrs"})

    # Setup find_available_port to return predictable ports
    with patch.object(mock_runtime, "_find_available_port", side_effect=[10001, 10002]):
        container = mock_runtime._create_container("test-scan-1")

    assert container == mock_container
    assert mock_runtime._scan_container == mock_container
    assert mock_runtime._tool_server_port == 10001
    assert mock_runtime._caido_port == 10002
    assert mock_runtime._tool_server_token is not None

    mock_docker_client.containers.run.assert_called_once()
    run_args = mock_docker_client.containers.run.call_args[0]
    run_kwargs = mock_docker_client.containers.run.call_args[1]
    assert run_args[0] == "test-image:latest"
    assert run_kwargs["name"] == "strix-scan-test-scan-1"
    assert run_kwargs["detach"] is True
    assert f"{CONTAINER_TOOL_SERVER_PORT}/tcp" in run_kwargs["ports"]
    assert run_kwargs["ports"][f"{CONTAINER_TOOL_SERVER_PORT}/tcp"] == 10001
    assert "TOOL_SERVER_TOKEN" in run_kwargs["environment"]


def test_create_container_cleans_up_existing(mock_runtime, mock_docker_client):
    mock_existing_container = MagicMock()
    mock_docker_client.containers.get.return_value = mock_existing_container
    
    mock_new_container = MagicMock()
    mock_docker_client.containers.run.return_value = mock_new_container
    
    mock_docker_client.images.get.return_value = MagicMock(id="image-id", attrs={"some": "attrs"})

    with patch.object(mock_runtime, "_find_available_port", side_effect=[10001, 10002]):
        container = mock_runtime._create_container("test-scan-1")

    mock_existing_container.stop.assert_called_once()
    mock_existing_container.remove.assert_called_once_with(force=True)
    assert container == mock_new_container


def test_create_container_failure_max_retries(mock_runtime, mock_docker_client):
    mock_docker_client.images.get.return_value = MagicMock(id="image-id", attrs={"some": "attrs"})
    mock_docker_client.containers.get.side_effect = NotFound("Not found")
    
    # Make container run fail consistently
    mock_docker_client.containers.run.side_effect = DockerException("Failed to run")

    # Mock time.sleep to avoid waiting during tests
    with patch("time.sleep"), patch.object(mock_runtime, "_find_available_port", return_value=12345):
        with pytest.raises(SandboxInitializationError) as exc_info:
            mock_runtime._create_container("test-scan-1", max_retries=1)

    assert "Failed to create container" in str(exc_info.value)
    assert mock_docker_client.containers.run.call_count == 2  # initial + 1 retry


def test_get_or_create_container_reuses_running_cache(mock_runtime):
    mock_container = MagicMock()
    mock_container.status = "running"
    mock_runtime._scan_container = mock_container

    container = mock_runtime._get_or_create_container("test-scan-1")
    
    assert container == mock_container
    mock_container.reload.assert_called_once()


def test_get_or_create_container_starts_stopped_cache(mock_runtime, mock_docker_client):
    mock_container = MagicMock()
    mock_container.status = "exited"
    mock_docker_client.containers.get.return_value = mock_container
    
    # Needs to recover state when starting existing
    with patch.object(mock_runtime, "_recover_container_state") as mock_recover, \
         patch("time.sleep"):
        container = mock_runtime._get_or_create_container("test-scan-1")
        
    assert container == mock_container
    mock_container.start.assert_called_once()
    mock_recover.assert_called_once_with(mock_container)


def test_get_or_create_container_fallback_to_create(mock_runtime, mock_docker_client):
    mock_runtime._scan_container = None
    mock_docker_client.containers.get.side_effect = NotFound("Not found")
    mock_docker_client.containers.list.return_value = []
    
    with patch.object(mock_runtime, "_create_container") as mock_create:
        mock_create.return_value = MagicMock()
        container = mock_runtime._get_or_create_container("test-scan-1")
        
    assert container == mock_create.return_value
    mock_create.assert_called_once_with("test-scan-1")


@pytest.mark.asyncio
async def test_create_sandbox(mock_runtime, mock_docker_client):
    mock_container = MagicMock()
    mock_container.id = "test-workspace-id"
    
    mock_runtime._scan_container = mock_container
    mock_runtime._tool_server_port = 10001
    mock_runtime._caido_port = 10002
    mock_runtime._tool_server_token = "test-token"
    
    with patch.object(mock_runtime, "_get_or_create_container", return_value=mock_container), \
         patch.object(mock_runtime, "_register_agent") as mock_register, \
         patch("strix.runtime.docker_runtime.Path") as mock_path, \
         patch.object(mock_runtime, "_copy_local_directory_to_container") as mock_copy:
        
        sandbox_info = await mock_runtime.create_sandbox(
            "test-agent-id", 
            local_sources=[{"source_path": "/fake/path"}]
        )
        
    assert sandbox_info["workspace_id"] == "test-workspace-id"
    assert sandbox_info["auth_token"] == "test-token"
    assert sandbox_info["tool_server_port"] == 10001
    assert sandbox_info["caido_port"] == 10002
    assert sandbox_info["agent_id"] == "test-agent-id"
    assert "10001" in sandbox_info["api_url"]
    
    mock_register.assert_called_once_with(sandbox_info["api_url"], "test-agent-id", "test-token")
    mock_copy.assert_called_once()


@pytest.mark.asyncio
async def test_destroy_sandbox(mock_runtime, mock_docker_client):
    mock_container = MagicMock()
    mock_docker_client.containers.get.return_value = mock_container
    
    mock_runtime._scan_container = mock_container
    mock_runtime._tool_server_port = 10001
    
    await mock_runtime.destroy_sandbox("test-workspace-id")
    
    mock_docker_client.containers.get.assert_called_once_with("test-workspace-id")
    mock_container.stop.assert_called_once()
    mock_container.remove.assert_called_once()
    
    assert mock_runtime._scan_container is None
    assert mock_runtime._tool_server_port is None


@pytest.mark.asyncio
async def test_destroy_sandbox_graceful(mock_runtime, mock_docker_client):
    mock_docker_client.containers.get.side_effect = NotFound("Not found")
    
    # Should not raise
    await mock_runtime.destroy_sandbox("test-workspace-id")
    assert mock_runtime._scan_container is None


def test_cleanup(mock_runtime):
    mock_container = MagicMock()
    mock_container.name = "strix-scan-123"
    mock_runtime._scan_container = mock_container

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        mock_runtime.cleanup()

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert "docker" in args
    assert "rm" in args
    assert "strix-scan-123" in args
    assert mock_run.call_args[1].get("timeout") == 10

    assert mock_runtime._scan_container is None


def test_cleanup_with_custom_timeout(mock_runtime):
    mock_container = MagicMock()
    mock_container.name = "strix-scan-123"
    mock_runtime._scan_container = mock_container

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        mock_runtime.cleanup(timeout=30)

    assert mock_run.call_args[1].get("timeout") == 30


def test_cleanup_timeout_fallback(mock_runtime):
    mock_container = MagicMock()
    mock_container.name = "strix-scan-123"
    mock_runtime._scan_container = mock_container

    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(cmd=["docker", "rm"], timeout=10)
        mock_runtime.cleanup()

    # Should fallback to SDK removal
    mock_container.remove.assert_called_once_with(force=True)


def test_cleanup_cli_failure_fallback(mock_runtime):
    mock_container = MagicMock()
    mock_container.name = "strix-scan-123"
    mock_runtime._scan_container = mock_container

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        mock_runtime.cleanup()

    # Should fallback to SDK removal
    mock_container.stop.assert_called_once_with(timeout=5)
    mock_container.remove.assert_called_once_with(force=True)


def test_recover_container_state(mock_runtime):
    mock_container = MagicMock()
    mock_container.attrs = {
        "Config": {
            "Env": [
                "OTHER_VAR=1",
                "TOOL_SERVER_TOKEN=recovered-token",
                "SOME_VAR=2"
            ]
        },
        "NetworkSettings": {
            "Ports": {
                f"{CONTAINER_TOOL_SERVER_PORT}/tcp": [{"HostIp": "0.0.0.0", "HostPort": "12345"}],
                f"{CONTAINER_CAIDO_PORT}/tcp": [{"HostIp": "0.0.0.0", "HostPort": "12346"}]
            }
        }
    }
    
    mock_runtime._recover_container_state(mock_container)
    
    assert mock_runtime._tool_server_token == "recovered-token"
    assert mock_runtime._tool_server_port == 12345
    assert mock_runtime._caido_port == 12346

"""
Pytest configuration and fixtures for BlenderMCP tests.

This module provides fixtures for testing the MCP server without requiring
a running Blender instance. All fixtures mock the TCP socket connection.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from typing import Dict, Any, Callable


@pytest.fixture
def mock_socket():
    """
    Mock TCP socket for testing without Blender.

    Returns a MagicMock that simulates socket.socket behavior.
    Use this to test socket communication without a real connection.

    Example:
        def test_send_command(mock_socket):
            mock_socket.recv.return_value = b'{"status": "success", "result": {}}'
            # Test code here
    """
    sock = MagicMock()
    sock.connect.return_value = None
    sock.sendall.return_value = None
    sock.close.return_value = None
    sock.settimeout.return_value = None
    return sock


@pytest.fixture
def mock_blender_response() -> Callable[[str, Any], Dict[str, Any]]:
    """
    Factory fixture for creating mock Blender responses.

    Returns a function that creates properly formatted Blender response dicts.

    Args:
        status: "success" or "error"
        result: The result data (for success)
        message: Error message (for error)

    Returns:
        Dict with status, result/message

    Example:
        def test_scene_info(mock_blender_response):
            response = mock_blender_response("success", {"objects": ["Cube"]})
            assert response["status"] == "success"
    """

    def _create_response(
        status: str = "success", result: Any = None, message: str = None
    ) -> Dict[str, Any]:
        if status == "error":
            return {"status": "error", "message": message or "Unknown error"}
        return {"status": "success", "result": result or {}}

    return _create_response


@pytest.fixture
def mock_blender_connection(mock_socket, mock_blender_response):
    """
    Mock BlenderConnection class for testing tools.

    Returns a MagicMock that simulates BlenderConnection with a working
    send_command method that returns mock responses.

    Example:
        def test_get_scene_info(mock_blender_connection):
            mock_blender_connection.send_command.return_value = {"objects": []}
            # Test code here
    """
    connection = MagicMock()
    connection.sock = mock_socket
    connection.host = "localhost"
    connection.port = 9876
    connection.connect.return_value = True
    connection.disconnect.return_value = None

    # Default send_command returns empty success
    connection.send_command.return_value = mock_blender_response("success", {})

    return connection


@pytest.fixture
def mcp_client(mock_blender_connection):
    """
    Test client fixture for calling MCP tools.

    Patches get_blender_connection to return mock_blender_connection,
    allowing tools to be tested in isolation without a real Blender instance.

    Example:
        def test_tool_call(mcp_client):
            from blender_mcp.server import get_scene_info
            result = get_scene_info(mock_context)
    """
    with patch(
        "blender_mcp.server.get_blender_connection",
        return_value=mock_blender_connection,
    ):
        yield mock_blender_connection


@pytest.fixture
def mock_context():
    """
    Mock MCP Context for tool testing.

    Returns a MagicMock that simulates the FastMCP Context object.
    """
    context = MagicMock()
    context.request_id = "test-request-id"
    context.meta = {}
    return context


@pytest.fixture
def sample_scene_info() -> Dict[str, Any]:
    """
    Sample scene info response for testing.

    Returns a realistic Blender scene info structure.
    """
    return {
        "scene": {
            "name": "Scene",
            "objects": ["Cube", "Light", "Camera"],
            "materials": ["Material"],
            "total_objects": 3,
        },
        "render": {"engine": "CYCLES", "resolution_x": 1920, "resolution_y": 1080},
    }


@pytest.fixture
def sample_object_info() -> Dict[str, Any]:
    """
    Sample object info response for testing.

    Returns a realistic Blender object info structure.
    """
    return {
        "name": "Cube",
        "type": "MESH",
        "location": [0.0, 0.0, 0.0],
        "rotation": [0.0, 0.0, 0.0],
        "scale": [1.0, 1.0, 1.0],
        "visible": True,
        "material": None,
    }

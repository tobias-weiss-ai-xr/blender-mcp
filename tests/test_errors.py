"""
Tests for structured error types.

This module tests:
- BlenderMCPError: Base exception class
- Error subclasses: NodeNotFoundError, InvalidInputError, etc.
- format_error_response: Error response formatting
"""

import pytest

from blender_mcp.errors import (
    BlenderMCPError,
    NodeNotFoundError,
    InvalidInputError,
    BlenderError,
    TimeoutError,
    ConnectionError,
    format_error_response,
)


class TestBlenderMCPError:
    """Tests for the base BlenderMCPError class."""

    def test_blender_mcp_error_creation(self):
        """Test creating a BlenderMCPError."""
        error = BlenderMCPError("Something went wrong")

        assert error.message == "Something went wrong"
        assert str(error) == "Something went wrong"

    def test_blender_mcp_error_default_code(self):
        """Test default error code is UNKNOWN_ERROR."""
        error = BlenderMCPError("Test error")

        assert error.code == "UNKNOWN_ERROR"


class TestNodeNotFoundError:
    """Tests for NodeNotFoundError."""

    def test_node_not_found_error(self):
        """Test creating a NodeNotFoundError."""
        error = NodeNotFoundError("Material Output")

        assert error.code == "NODE_NOT_FOUND"
        assert "Material Output" in error.message

    def test_node_not_found_is_subclass(self):
        """Test NodeNotFoundError is a subclass of BlenderMCPError."""
        error = NodeNotFoundError("Test")

        assert isinstance(error, BlenderMCPError)
        assert isinstance(error, Exception)


class TestInvalidInputError:
    """Tests for InvalidInputError."""

    def test_invalid_input_error(self):
        """Test creating an InvalidInputError."""
        error = InvalidInputError("Value must be positive")

        assert error.code == "INVALID_INPUT"
        assert error.message == "Value must be positive"


class TestBlenderError:
    """Tests for BlenderError."""

    def test_blender_error(self):
        """Test creating a BlenderError."""
        error = BlenderError("Failed to create object")

        assert error.code == "BLENDER_ERROR"
        assert error.message == "Failed to create object"


class TestTimeoutError:
    """Tests for TimeoutError."""

    def test_timeout_error(self):
        """Test creating a TimeoutError."""
        error = TimeoutError("Operation timed out after 30s")

        assert error.code == "TIMEOUT"
        assert error.message == "Operation timed out after 30s"


class TestConnectionError:
    """Tests for ConnectionError."""

    def test_connection_error(self):
        """Test creating a ConnectionError."""
        error = ConnectionError("Socket connection refused")

        assert error.code == "CONNECTION_ERROR"
        assert error.message == "Socket connection refused"


class TestFormatErrorResponse:
    """Tests for format_error_response function."""

    def test_format_error_response_basic(self):
        """Test basic error response formatting."""
        error = BlenderMCPError("Test error")
        response = format_error_response(error)

        assert response["success"] is False
        assert response["error"]["code"] == "UNKNOWN_ERROR"
        assert response["error"]["message"] == "Test error"

    def test_format_error_response_node_not_found(self):
        """Test format_error_response with NodeNotFoundError."""
        error = NodeNotFoundError("MyNode")
        response = format_error_response(error)

        assert response["success"] is False
        assert response["error"]["code"] == "NODE_NOT_FOUND"
        assert "MyNode" in response["error"]["message"]

    def test_format_error_response_invalid_input(self):
        """Test format_error_response with InvalidInputError."""
        error = InvalidInputError("Invalid parameter")
        response = format_error_response(error)

        assert response["error"]["code"] == "INVALID_INPUT"
        assert response["error"]["message"] == "Invalid parameter"

    def test_format_error_response_blender_error(self):
        """Test format_error_response with BlenderError."""
        error = BlenderError("Operation failed")
        response = format_error_response(error)

        assert response["error"]["code"] == "BLENDER_ERROR"

    def test_format_error_response_timeout(self):
        """Test format_error_response with TimeoutError."""
        error = TimeoutError("Timed out")
        response = format_error_response(error)

        assert response["error"]["code"] == "TIMEOUT"

    def test_format_error_response_connection(self):
        """Test format_error_response with ConnectionError."""
        error = ConnectionError("Connection refused")
        response = format_error_response(error)

        assert response["error"]["code"] == "CONNECTION_ERROR"

    def test_format_error_response_structure(self):
        """Test format_error_response returns correct structure."""
        error = BlenderMCPError("Test")
        response = format_error_response(error)

        # Check required keys
        assert "success" in response
        assert "error" in response
        assert "code" in response["error"]
        assert "message" in response["error"]

        # Check values
        assert response["success"] is False
        assert isinstance(response["error"]["code"], str)
        assert isinstance(response["error"]["message"], str)

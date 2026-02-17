"""
Tests for standard response formatting.

This module tests:
- success_response: Creating success response dicts
- error_response: Creating error response dicts
- error_from_exception: Creating error responses from exceptions
"""

import pytest

from blender_mcp.responses import success_response, error_response, error_from_exception
from blender_mcp.errors import (
    BlenderMCPError,
    NodeNotFoundError,
    InvalidInputError,
    BlenderError,
    TimeoutError,
    ConnectionError,
    format_error_response,
)


class TestSuccessResponse:
    """Tests for success_response function."""

    def test_success_response_without_result(self):
        """Test success_response with no result argument."""
        response = success_response()

        assert response == {"success": True}
        assert "result" not in response

    def test_success_response_with_none_result(self):
        """Test success_response explicitly passed None."""
        response = success_response(None)

        assert response == {"success": True}
        assert "result" not in response

    def test_success_response_with_dict_result(self):
        """Test success_response with a dict result."""
        response = success_response({"count": 5, "name": "test"})

        assert response["success"] is True
        assert response["result"]["count"] == 5
        assert response["result"]["name"] == "test"

    def test_success_response_with_list_result(self):
        """Test success_response with a list result."""
        response = success_response([1, 2, 3])

        assert response["success"] is True
        assert response["result"] == [1, 2, 3]

    def test_success_response_with_string_result(self):
        """Test success_response with a string result."""
        response = success_response("Operation completed")

        assert response["success"] is True
        assert response["result"] == "Operation completed"

    def test_success_response_with_nested_dict(self):
        """Test success_response with nested dictionary."""
        nested = {"data": {"items": [{"id": 1}, {"id": 2}], "meta": {"total": 2}}}
        response = success_response(nested)

        assert response["success"] is True
        assert response["result"]["data"]["items"][0]["id"] == 1

    def test_success_response_with_empty_dict(self):
        """Test success_response with empty dict result."""
        response = success_response({})

        assert response["success"] is True
        assert response["result"] == {}


class TestErrorResponse:
    """Tests for error_response function."""

    def test_error_response_basic(self):
        """Test basic error_response creation."""
        response = error_response("ERROR_CODE", "Something went wrong")

        assert response["success"] is False
        assert response["error"]["code"] == "ERROR_CODE"
        assert response["error"]["message"] == "Something went wrong"

    def test_error_response_node_not_found(self):
        """Test error_response for node not found error."""
        response = error_response(
            "NODE_NOT_FOUND", "Node 'Material Output' does not exist"
        )

        assert response["success"] is False
        assert response["error"]["code"] == "NODE_NOT_FOUND"
        assert "Material Output" in response["error"]["message"]

    def test_error_response_invalid_input(self):
        """Test error_response for invalid input error."""
        response = error_response("INVALID_INPUT", "Object name cannot be empty")

        assert response["success"] is False
        assert response["error"]["code"] == "INVALID_INPUT"
        assert response["error"]["message"] == "Object name cannot be empty"

    def test_error_response_structure(self):
        """Test error_response has correct structure."""
        response = error_response("TEST_CODE", "Test message")

        # Check top-level keys
        assert "success" in response
        assert "error" in response

        # Check error object keys
        assert "code" in response["error"]
        assert "message" in response["error"]
        assert len(response["error"]) == 2

    def test_error_response_with_empty_message(self):
        """Test error_response with empty message."""
        response = error_response("EMPTY_MSG", "")

        assert response["success"] is False
        assert response["error"]["message"] == ""


class TestErrorFromException:
    """Tests for error_from_exception function."""

    def test_error_from_custom_exception(self):
        """Test error_from_exception with BlenderMCPError subclass."""
        error = NodeNotFoundError("Material Output")
        response = error_from_exception(error)

        assert response["success"] is False
        assert response["error"]["code"] == "NODE_NOT_FOUND"
        assert "Material Output" in response["error"]["message"]

    def test_error_from_node_not_found_error(self):
        """Test error_from_exception with NodeNotFoundError."""
        error = NodeNotFoundError("MyNode")
        response = error_from_exception(error)

        assert response["error"]["code"] == "NODE_NOT_FOUND"
        assert "MyNode" in response["error"]["message"]

    def test_error_from_invalid_input_error(self):
        """Test error_from_exception with InvalidInputError."""
        error = InvalidInputError("Invalid value provided")
        response = error_from_exception(error)

        assert response["error"]["code"] == "INVALID_INPUT"
        assert response["error"]["message"] == "Invalid value provided"

    def test_error_from_blender_error(self):
        """Test error_from_exception with BlenderError."""
        error = BlenderError("Failed to create object")
        response = error_from_exception(error)

        assert response["error"]["code"] == "BLENDER_ERROR"
        assert response["error"]["message"] == "Failed to create object"

    def test_error_from_timeout_error(self):
        """Test error_from_exception with TimeoutError."""
        error = TimeoutError("Operation timed out")
        response = error_from_exception(error)

        assert response["error"]["code"] == "TIMEOUT"
        assert response["error"]["message"] == "Operation timed out"

    def test_error_from_connection_error(self):
        """Test error_from_exception with ConnectionError."""
        error = ConnectionError("Socket connection refused")
        response = error_from_exception(error)

        assert response["error"]["code"] == "CONNECTION_ERROR"
        assert response["error"]["message"] == "Socket connection refused"

    def test_error_from_standard_exception(self):
        """Test error_from_exception with standard Python exception."""
        error = ValueError("Something went wrong")
        response = error_from_exception(error)

        # Should fallback to INTERNAL_ERROR
        assert response["success"] is False
        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert response["error"]["message"] == "Something went wrong"

    def test_error_from_runtime_error(self):
        """Test error_from_exception with RuntimeError."""
        error = RuntimeError("Unexpected runtime issue")
        response = error_from_exception(error)

        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert "Unexpected runtime issue" in response["error"]["message"]

    def test_error_from_key_error(self):
        """Test error_from_exception with KeyError."""
        error = KeyError("missing_key")
        response = error_from_exception(error)

        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert "missing_key" in response["error"]["message"]

    def test_error_from_type_error(self):
        """Test error_from_exception with TypeError."""
        error = TypeError("Expected string, got int")
        response = error_from_exception(error)

        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert "Expected string, got int" in response["error"]["message"]

    def test_error_from_exception_with_none_message(self):
        """Test error_from_exception handles exception with empty str."""
        error = ValueError("")
        response = error_from_exception(error)

        assert response["error"]["code"] == "INTERNAL_ERROR"
        assert response["error"]["message"] == ""

    def test_error_from_base_blender_mcp_error(self):
        """Test error_from_exception with base BlenderMCPError."""
        error = BlenderMCPError("Generic error")
        response = error_from_exception(error)

        assert response["error"]["code"] == "UNKNOWN_ERROR"
        assert response["error"]["message"] == "Generic error"


class TestResponseIntegration:
    """Integration tests for response helpers with errors module."""

    def test_error_from_exception_matches_format_error_response(self):
        """Test that error_from_exception produces same format as error_response."""
        error = NodeNotFoundError("TestNode")
        response1 = error_from_exception(error)
        response2 = error_response("NODE_NOT_FOUND", "TestNode")

        assert response1 == response2

    def test_success_and_error_responses_are_distinct(self):
        """Test that success and error responses have different structures."""
        success = success_response({"data": "value"})
        error = error_response("CODE", "message")

        assert success["success"] is True
        assert error["success"] is False
        assert "result" in success
        assert "error" in error

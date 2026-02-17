"""
Structured error types for Blender MCP.

This module provides a consistent error handling system with:
- Hierarchical exception classes
- Standard error codes
- Unified error response formatting
"""


class BlenderMCPError(Exception):
    """Base exception for all Blender MCP errors.

    All custom exceptions in Blender MCP should inherit from this class.
    Provides a consistent interface with error codes and messages.
    """

    code = "UNKNOWN_ERROR"

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NodeNotFoundError(BlenderMCPError):
    """Node or node tree doesn't exist.

    Raised when attempting to access or modify a node or node tree
    that cannot be found in the current Blender context.
    """

    code = "NODE_NOT_FOUND"


class InvalidInputError(BlenderMCPError):
    """Input validation failed.

    Raised when provided parameters fail validation, such as:
    - Invalid parameter types
    - Values out of acceptable range
    - Missing required parameters
    """

    code = "INVALID_INPUT"


class BlenderError(BlenderMCPError):
    """Blender operation failed.

    Raised when a Blender API operation fails, such as:
    - Object creation/deletion failures
    - Material application errors
    - Scene manipulation issues
    """

    code = "BLENDER_ERROR"


class TimeoutError(BlenderMCPError):
    """Operation timed out.

    Raised when an operation exceeds the allowed time limit,
    typically due to complex operations or unresponsive Blender state.
    """

    code = "TIMEOUT"


class ConnectionError(BlenderMCPError):
    """Socket connection failed.

    Raised when communication with the Blender addon fails, such as:
    - Socket connection refused
    - Broken pipe errors
    - Connection reset by peer
    """

    code = "CONNECTION_ERROR"


def format_error_response(error: BlenderMCPError) -> dict:
    """Format an error as a standard response dict.

    Args:
        error: A BlenderMCPError instance (or subclass)

    Returns:
        A dictionary with the standard error response format:
        {
            "success": False,
            "error": {
                "code": "<ERROR_CODE>",
                "message": "<error message>"
            }
        }

    Example:
        >>> err = NodeNotFoundError("Material 'MyMat' not found")
        >>> format_error_response(err)
        {'success': False, 'error': {'code': 'NODE_NOT_FOUND', 'message': "Material 'MyMat' not found"}}
    """
    return {"success": False, "error": {"code": error.code, "message": error.message}}

"""
Standard response formatting for Blender MCP tools.

All new tools should use these helpers to ensure consistent response formats.

Success Response Format:
    {"success": true, "result": {...}}

Error Response Format:
    {"success": false, "error": {"code": "...", "message": "..."}}

Usage:
    from blender_mcp.responses import success_response, error_response, error_from_exception

    # Success case
    return success_response({"vertices": 100, "faces": 50})

    # Error case
    return error_response("NODE_NOT_FOUND", f"Node '{name}' does not exist")

    # From exception
    try:
        ...
    except BlenderMCPError as e:
        return error_from_exception(e)
"""

from typing import Any, Optional


def success_response(result: Any = None) -> dict:
    """
    Create a standard success response.

    Args:
        result: The result data to return (can be dict, list, str, etc.)

    Returns:
        dict with success=True and optional result

    Examples:
        >>> success_response()
        {"success": True}

        >>> success_response({"count": 5})
        {"success": True, "result": {"count": 5}}

        >>> success_response("Operation completed")
        {"success": True, "result": "Operation completed"}
    """
    response = {"success": True}
    if result is not None:
        response["result"] = result
    return response


def error_response(error_code: str, message: str) -> dict:
    """
    Create a standard error response.

    Args:
        error_code: Error code string (e.g., "NODE_NOT_FOUND", "INVALID_INPUT")
        message: Human-readable error message describing what went wrong

    Returns:
        dict with success=False and error details

    Examples:
        >>> error_response("NODE_NOT_FOUND", "Node 'Material Output' does not exist")
        {"success": False, "error": {"code": "NODE_NOT_FOUND", "message": "Node 'Material Output' does not exist"}}

        >>> error_response("INVALID_INPUT", "Object name cannot be empty")
        {"success": False, "error": {"code": "INVALID_INPUT", "message": "Object name cannot be empty"}}
    """
    return {"success": False, "error": {"code": error_code, "message": message}}


def error_from_exception(error: Exception) -> dict:
    """
    Create an error response from an exception.

    Intended for use with custom exceptions from errors.py that have
    `code` and `message` attributes. Falls back to INTERNAL_ERROR
    for standard Python exceptions.

    Args:
        error: Exception instance (preferably from errors.py with code/message attributes)

    Returns:
        dict with success=False and error details

    Examples:
        >>> from blender_mcp.errors import NodeNotFoundError
        >>> try:
        ...     raise NodeNotFoundError("Material Output")
        ... except NodeNotFoundError as e:
        ...     return error_from_exception(e)
        {"success": False, "error": {"code": "NODE_NOT_FOUND", "message": "Node 'Material Output' not found"}}

        >>> try:
        ...     raise ValueError("Something went wrong")
        ... except Exception as e:
        ...     return error_from_exception(e)
        {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Something went wrong"}}
    """
    if hasattr(error, "code") and hasattr(error, "message"):
        return error_response(error.code, error.message)
    return error_response("INTERNAL_ERROR", str(error))

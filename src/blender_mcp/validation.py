"""
Input validation for Blender MCP tools using Pydantic.

This module provides base validation infrastructure for tool parameters.
New tools can extend BaseToolParams for automatic input validation.
"""

from pydantic import BaseModel
from typing import Optional, Any, Callable
from functools import wraps


class BaseToolParams(BaseModel):
    """
    Base model for tool parameters.

    Can be extended by specific tools to add their own validated fields.
    Common fields can be added here as the project evolves.

    Example:
        class CreateCubeParams(BaseToolParams):
            name: str
            size: float = 1.0
            location: tuple[float, float, float] = (0, 0, 0)
    """

    pass


def validated(params_model: type[BaseModel]) -> Callable:
    """
    Decorator stub for automatic parameter validation.

    Future implementation will validate tool inputs against a Pydantic model
    before executing the tool function.

    Args:
        params_model: Pydantic model class to validate parameters against

    Returns:
        Decorator function

    Example (future usage):
        @validated(CreateCubeParams)
        def create_cube(params: CreateCubeParams) -> dict:
            # params is already validated
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Implement validation logic
            # For now, just pass through to the function
            return func(*args, **kwargs)

        return wrapper

    return decorator

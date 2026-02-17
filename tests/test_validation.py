"""
Tests for input validation infrastructure.

This module tests:
- BaseToolParams: Base model for tool parameters
- @validated decorator: Parameter validation decorator (stub)
"""

import pytest
from pydantic import ValidationError

from blender_mcp.validation import BaseToolParams, validated


class TestBaseToolParams:
    """Tests for BaseToolParams Pydantic model."""

    def test_base_tool_params_can_be_instantiated(self):
        """Test that BaseToolParams can be instantiated."""
        params = BaseToolParams()
        assert params is not None

    def test_base_tool_params_is_empty_by_default(self):
        """Test that BaseToolParams has no required fields."""
        params = BaseToolParams()
        # Should have no fields set
        assert params.model_dump() == {}

    def test_base_tool_params_can_be_extended(self):
        """Test that BaseToolParams can be extended with custom fields."""

        class CustomParams(BaseToolParams):
            name: str
            value: int = 10

        params = CustomParams(name="test")
        assert params.name == "test"
        assert params.value == 10

    def test_base_tool_params_validation_with_custom_model(self):
        """Test that extended models validate correctly."""

        class StrictParams(BaseToolParams):
            count: int

            class Config:
                extra = "forbid"

        # Valid params
        params = StrictParams(count=5)
        assert params.count == 5

        # Invalid: missing required field
        with pytest.raises(ValidationError):
            StrictParams()

    def test_base_tool_params_with_complex_types(self):
        """Test BaseToolParams extension with complex type hints."""

        class ComplexParams(BaseToolParams):
            items: list[str]
            mapping: dict[str, int]
            location: tuple[float, float, float] = (0.0, 0.0, 0.0)

        params = ComplexParams(items=["a", "b"], mapping={"x": 1})
        assert params.items == ["a", "b"]
        assert params.mapping == {"x": 1}
        assert params.location == (0.0, 0.0, 0.0)

    def test_base_tool_params_optional_fields(self):
        """Test BaseToolParams extension with optional fields."""

        class OptionalParams(BaseToolParams):
            required: str
            optional: str | None = None

        # Without optional field
        params1 = OptionalParams(required="value")
        assert params1.required == "value"
        assert params1.optional is None

        # With optional field
        params2 = OptionalParams(required="value", optional="extra")
        assert params2.optional == "extra"

    def test_base_tool_params_model_dump(self):
        """Test that model_dump works correctly on extended models."""

        class ExampleParams(BaseToolParams):
            name: str
            size: float = 1.0

        params = ExampleParams(name="test", size=2.5)
        dump = params.model_dump()

        assert dump == {"name": "test", "size": 2.5}

    def test_base_tool_params_model_validate(self):
        """Test model_validate for creating from dict."""

        class ExampleParams(BaseToolParams):
            name: str
            count: int = 0

        params = ExampleParams.model_validate({"name": "test", "count": 5})
        assert params.name == "test"
        assert params.count == 5


class TestValidatedDecorator:
    """Tests for the @validated decorator (stub implementation)."""

    def test_validated_passes_through_function(self):
        """Test that @validated decorator passes through the function call."""

        @validated(BaseToolParams)
        def simple_function(*args, **kwargs):
            return "result"

        result = simple_function()
        assert result == "result"

    def test_validated_preserves_function_args(self):
        """Test that @validated preserves function arguments."""

        @validated(BaseToolParams)
        def add(a, b):
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_validated_preserves_kwargs(self):
        """Test that @validated preserves keyword arguments."""

        @validated(BaseToolParams)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = greet("World", greeting="Hi")
        assert result == "Hi, World!"

    def test_validated_with_custom_model(self):
        """Test @validated with a custom Pydantic model."""

        class AddParams(BaseToolParams):
            a: int
            b: int

        @validated(AddParams)
        def add(a, b):
            return a + b

        # Stub implementation just passes through
        result = add(5, 10)
        assert result == 15

    def test_validated_preserves_function_name(self):
        """Test that @validated preserves function metadata."""

        @validated(BaseToolParams)
        def my_function():
            """My docstring."""
            pass

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_validated_returns_decorator(self):
        """Test that validated() returns a decorator function."""
        decorator = validated(BaseToolParams)
        assert callable(decorator)

    def test_validated_decorator_accepts_function(self):
        """Test that the returned decorator accepts a function."""

        def original_func():
            return "original"

        decorator = validated(BaseToolParams)
        wrapped = decorator(original_func)

        assert wrapped() == "original"

    def test_validated_with_exception_in_function(self):
        """Test that exceptions in wrapped function propagate correctly."""

        @validated(BaseToolParams)
        def raises_error():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            raises_error()

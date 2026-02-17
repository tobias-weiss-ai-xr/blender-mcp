"""
Tests for shader node MCP tools.

This module tests shader node operations including:
- create_material: Creating new materials
- link_shader_nodes: Creating connections between shader node sockets
"""

import json
import pytest
from unittest.mock import MagicMock, patch


class TestCreateMaterial:
    """Tests for the create_material MCP tool."""

    def test_create_material_success(self, mock_context, mock_blender_connection):
        """
        Test successful material creation.

        The tool should:
        1. Send a create_material command to Blender
        2. Return a success response with name and has_nodes
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "name": "TestMaterial",
            "has_nodes": True,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_material

            # Act: Call the tool
            result = create_material(ctx=mock_context, name="TestMaterial")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "create_material", {"name": "TestMaterial", "use_nodes": True}
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "TestMaterial"
            assert result_dict["result"]["has_nodes"] is True

    def test_create_material_without_nodes(self, mock_context, mock_blender_connection):
        """Test create_material with use_nodes=False."""
        # Arrange
        mock_blender_connection.send_command.return_value = {
            "name": "SimpleMaterial",
            "has_nodes": False,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_material

            # Act
            result = create_material(
                ctx=mock_context, name="SimpleMaterial", use_nodes=False
            )

            # Assert: Verify correct params sent
            mock_blender_connection.send_command.assert_called_once_with(
                "create_material", {"name": "SimpleMaterial", "use_nodes": False}
            )

            # Assert: Verify response
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "SimpleMaterial"
            assert result_dict["result"]["has_nodes"] is False


class TestLinkShaderNodes:
    """Tests for the link_shader_nodes MCP tool."""

    def test_link_shader_nodes_success(self, mock_context, mock_blender_connection):
        """
        Test successful link between two shader nodes.

        The tool should:
        1. Send a link_shader_nodes command to Blender
        2. Return a success response with linked=true
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {"linked": True}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import the tool after patching
            from blender_mcp.server import link_shader_nodes

            # Act: Call the tool
            result = link_shader_nodes(
                ctx=mock_context,
                material_name="TestMaterial",
                from_node="Diffuse BSDF",
                from_socket="Color",
                to_node="Material Output",
                to_socket="Surface",
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "link_shader_nodes",
                {
                    "material_name": "TestMaterial",
                    "from_node": "Diffuse BSDF",
                    "from_socket": "Color",
                    "to_node": "Material Output",
                    "to_socket": "Surface",
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["linked"] is True

    def test_link_shader_nodes_missing_from_node(
        self, mock_context, mock_blender_connection
    ):
        """
        Test linking when from_node doesn't exist.

        The tool should return NodeNotFoundError when the source node is not found.
        """
        # Arrange: Mock Blender to return an error for missing node
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Node 'NonExistentNode' not found in material 'TestMaterial'",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import link_shader_nodes

            # Act
            result = link_shader_nodes(
                ctx=mock_context,
                material_name="TestMaterial",
                from_node="NonExistentNode",
                from_socket="Color",
                to_node="Material Output",
                to_socket="Surface",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"

    def test_link_shader_nodes_missing_to_node(
        self, mock_context, mock_blender_connection
    ):
        """
        Test linking when to_node doesn't exist.

        The tool should return NodeNotFoundError when the destination node is not found.
        """
        # Arrange: Mock Blender to return an error for missing node
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Node 'MissingOutput' not found in material 'TestMaterial'",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import link_shader_nodes

            # Act
            result = link_shader_nodes(
                ctx=mock_context,
                material_name="TestMaterial",
                from_node="Diffuse BSDF",
                from_socket="Color",
                to_node="MissingOutput",
                to_socket="Surface",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"


class TestListMaterials:
    """Tests for the list_materials MCP tool."""

    def test_list_materials_success(self, mock_context, mock_blender_connection):
        """
        Test successful listing of all materials.

        The tool should:
        1. Send a list_materials command to Blender
        2. Return a success response with a list of materials
        """
        # Arrange: Mock Blender to return materials list
        mock_blender_connection.send_command.return_value = {
            "materials": [
                {"name": "Material", "use_nodes": True, "users": 1},
                {"name": "RedMetal", "use_nodes": True, "users": 2},
                {"name": "BlueGlass", "use_nodes": False, "users": 0},
            ]
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import the tool after patching
            from blender_mcp.server import list_materials

            # Act: Call the tool
            result = list_materials(ctx=mock_context)

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "list_materials", {}
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "materials" in result_dict["result"]
            assert len(result_dict["result"]["materials"]) == 3
            assert result_dict["result"]["materials"][0]["name"] == "Material"
            assert result_dict["result"]["materials"][0]["use_nodes"] is True
            assert result_dict["result"]["materials"][0]["users"] == 1

    def test_list_materials_empty(self, mock_context, mock_blender_connection):
        """
        Test listing materials when none exist.

        The tool should return an empty list.
        """
        # Arrange: Mock Blender to return empty list
        mock_blender_connection.send_command.return_value = {"materials": []}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import list_materials

            # Act
            result = list_materials(ctx=mock_context)

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["materials"] == []


class TestDeleteMaterial:
    """Tests for the delete_material MCP tool."""

    def test_delete_material_success(self, mock_context, mock_blender_connection):
        """
        Test successful deletion of an existing material.

        The tool should:
        1. Send a delete_material command to Blender
        2. Return a success response with the deleted material name
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {"deleted": "TestMaterial"}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import the tool after patching
            from blender_mcp.server import delete_material

            # Act: Call the tool
            result = delete_material(
                ctx=mock_context,
                material_name="TestMaterial",
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "delete_material",
                {"material_name": "TestMaterial"},
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["deleted"] == "TestMaterial"

    def test_delete_material_not_found(self, mock_context, mock_blender_connection):
        """
        Test deleting a non-existent material.

        The tool should return NodeNotFoundError when the material is not found.
        """
        # Arrange: Mock Blender to return an error for missing material
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Material 'NonExistentMaterial' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import delete_material

            # Act
            result = delete_material(
                ctx=mock_context,
                material_name="NonExistentMaterial",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"


class TestAssignMaterial:
    """Tests for the assign_material MCP tool."""

    def test_assign_material_success(self, mock_context, mock_blender_connection):
        """
        Test successfully assigning a material to an object.

        The tool should:
        1. Send an assign_material command to Blender
        2. Return a success response with object, material, and slot info
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "object": "Cube",
            "material": "TestMaterial",
            "slot": 0,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import the tool after patching
            from blender_mcp.server import assign_material

            # Act: Call the tool
            result = assign_material(
                ctx=mock_context,
                object_name="Cube",
                material_name="TestMaterial",
                slot_index=0,
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "assign_material",
                {
                    "object_name": "Cube",
                    "material_name": "TestMaterial",
                    "slot_index": 0,
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["object"] == "Cube"
            assert result_dict["result"]["material"] == "TestMaterial"
            assert result_dict["result"]["slot"] == 0

    def test_assign_material_default_slot(self, mock_context, mock_blender_connection):
        """
        Test assigning material with default slot index.

        The tool should use slot_index=0 when not specified.
        """
        # Arrange
        mock_blender_connection.send_command.return_value = {
            "object": "Sphere",
            "material": "MyMaterial",
            "slot": 0,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import assign_material

            # Act: Call without slot_index (should default to 0)
            result = assign_material(
                ctx=mock_context,
                object_name="Sphere",
                material_name="MyMaterial",
            )

            # Assert: slot_index defaults to 0 if passed, or params include correct values
            call_args = mock_blender_connection.send_command.call_args
            # slot_index may or may not be in params depending on implementation
            # Check that the params are correct
            params = call_args[0][1] if call_args[0] else call_args[1]
            # Either slot_index is 0, or it wasn't passed (which is also valid for default)
            if "slot_index" in params:
                assert params["slot_index"] == 0

            # Assert: Success response
            result_dict = json.loads(result)
            assert result_dict["success"] is True

    def test_assign_material_missing_object(
        self, mock_context, mock_blender_connection
    ):
        """
        Test assigning when object doesn't exist.

        The tool should return NodeNotFoundError when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Object 'NonExistentObject' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import assign_material

            # Act
            result = assign_material(
                ctx=mock_context,
                object_name="NonExistentObject",
                material_name="TestMaterial",
                slot_index=0,
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"


class TestSetNodeProperty:
    """Tests for the set_node_property MCP tool."""

    def test_set_color_property_success(self, mock_context, mock_blender_connection):
        """Test setting a color property (RGBA) on a node."""
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "property": "Base Color",
            "value": [1.0, 0.0, 0.0, 1.0],
            "material_name": "Material",
            "node_name": "Principled BSDF",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="Material",
                node_name="Principled BSDF",
                property="Base Color",
                value=[1.0, 0.0, 0.0, 1.0],
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "set_node_property",
                {
                    "material_name": "Material",
                    "node_name": "Principled BSDF",
                    "property": "Base Color",
                    "value": [1.0, 0.0, 0.0, 1.0],
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["property"] == "Base Color"
            assert result_dict["result"]["value"] == [1.0, 0.0, 0.0, 1.0]

    def test_set_float_property_success(self, mock_context, mock_blender_connection):
        """Test setting a float property (metallic/roughness) on a node."""
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "property": "Metallic",
            "value": 0.8,
            "material_name": "Material",
            "node_name": "Principled BSDF",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="Material",
                node_name="Principled BSDF",
                property="Metallic",
                value=0.8,
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["property"] == "Metallic"
            assert result_dict["result"]["value"] == 0.8

    def test_set_roughness_property_success(
        self, mock_context, mock_blender_connection
    ):
        """Test setting roughness property on a Principled BSDF node."""
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "property": "Roughness",
            "value": 0.3,
            "material_name": "GlossyMat",
            "node_name": "Principled BSDF",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="GlossyMat",
                node_name="Principled BSDF",
                property="Roughness",
                value=0.3,
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["value"] == 0.3

    def test_set_ior_property_success(self, mock_context, mock_blender_connection):
        """Test setting IOR (Index of Refraction) property on a node."""
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "property": "IOR",
            "value": 1.45,
            "material_name": "GlassMat",
            "node_name": "Principled BSDF",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="GlassMat",
                node_name="Principled BSDF",
                property="IOR",
                value=1.45,
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["value"] == 1.45

    def test_set_node_property_material_not_found(
        self, mock_context, mock_blender_connection
    ):
        """Test error handling when material is not found."""
        # Arrange: Mock Blender to return error
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Material 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="NonExistent",
                node_name="Principled BSDF",
                property="Base Color",
                value=[1.0, 0.0, 0.0, 1.0],
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"

    def test_set_node_property_node_not_found(
        self, mock_context, mock_blender_connection
    ):
        """Test error handling when node is not found in material."""
        # Arrange: Mock Blender to return error
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Node 'NonExistentNode' not found in material 'Material'",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="Material",
                node_name="NonExistentNode",
                property="Base Color",
                value=[1.0, 0.0, 0.0, 1.0],
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"

    def test_set_node_property_invalid_property(
        self, mock_context, mock_blender_connection
    ):
        """Test error handling when property name is invalid."""
        # Arrange: Mock Blender to return error
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "INVALID_INPUT",
                "message": "Property 'InvalidProperty' not found on node 'Principled BSDF'",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_node_property

            # Act
            result = set_node_property(
                mock_context,
                material_name="Material",
                node_name="Principled BSDF",
                property="InvalidProperty",
                value=1.0,
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "INVALID_INPUT"


class TestCreateShaderNode:
    """Tests for the create_shader_node MCP tool."""

    def test_create_shader_node_success(self, mock_context, mock_blender_connection):
        """
        Test successful creation of a shader node.

        The tool should:
        1. Send a create_shader_node command to Blender
        2. Return a success response with node name and type
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "name": "Principled BSDF",
            "type": "BSDF_PRINCIPLED",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import the tool after patching
            from blender_mcp.server import create_shader_node

            # Act: Call the tool
            result = create_shader_node(
                ctx=mock_context,
                material_name="TestMaterial",
                node_type="BSDF_PRINCIPLED",
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "create_shader_node",
                {
                    "material_name": "TestMaterial",
                    "node_type": "BSDF_PRINCIPLED",
                    "name": None,
                    "location": [0, 0],
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "Principled BSDF"
            assert result_dict["result"]["type"] == "BSDF_PRINCIPLED"

    def test_create_shader_node_with_custom_name_and_location(
        self, mock_context, mock_blender_connection
    ):
        """
        Test creating a node with custom name and location.

        The tool should pass optional parameters correctly.
        """
        # Arrange
        mock_blender_connection.send_command.return_value = {
            "name": "MyCustomNode",
            "type": "TEX_IMAGE",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_shader_node

            # Act
            result = create_shader_node(
                ctx=mock_context,
                material_name="TestMaterial",
                node_type="TEX_IMAGE",
                name="MyCustomNode",
                location=[200, 300],
            )

            # Assert: Verify params passed correctly
            mock_blender_connection.send_command.assert_called_once_with(
                "create_shader_node",
                {
                    "material_name": "TestMaterial",
                    "node_type": "TEX_IMAGE",
                    "name": "MyCustomNode",
                    "location": [200, 300],
                },
            )

            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "MyCustomNode"

    def test_create_shader_node_invalid_type(
        self, mock_context, mock_blender_connection
    ):
        """
        Test creating a node with invalid type.

        The tool should return InvalidInputError when node_type is not in allowed list.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_shader_node

            # Act
            result = create_shader_node(
                ctx=mock_context,
                material_name="TestMaterial",
                node_type="INVALID_NODE_TYPE",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "INVALID_INPUT"

    def test_create_shader_node_all_supported_types(
        self, mock_context, mock_blender_connection
    ):
        """
        Test that all 10 supported node types work.

        Supported types: BSDF_PRINCIPLED, TEX_IMAGE, TEX_COORD, MAPPING, MIX,
                        NORMAL_MAP, OUTPUT_MATERIAL, MATH, RGB, VALUE
        """
        supported_types = [
            "BSDF_PRINCIPLED",
            "TEX_IMAGE",
            "TEX_COORD",
            "MAPPING",
            "MIX",
            "NORMAL_MAP",
            "OUTPUT_MATERIAL",
            "MATH",
            "RGB",
            "VALUE",
        ]

        for node_type in supported_types:
            mock_blender_connection.send_command.reset_mock()
            mock_blender_connection.send_command.return_value = {
                "name": f"Test_{node_type}",
                "type": node_type,
            }

            with patch(
                "blender_mcp.server.get_blender_connection",
                return_value=mock_blender_connection,
            ):
                from blender_mcp.server import create_shader_node

                # Act
                result = create_shader_node(
                    ctx=mock_context,
                    material_name="TestMaterial",
                    node_type=node_type,
                )

                # Assert
                result_dict = json.loads(result)
                assert result_dict["success"] is True, f"Failed for type {node_type}"
                assert result_dict["result"]["type"] == node_type


class TestGetNodeTree:
    """Tests for the get_node_tree MCP tool."""

    def test_get_node_tree_returns_nodes_and_links(
        self, mock_context, mock_blender_connection
    ):
        """
        Test that get_node_tree returns a structured response with nodes and links.

        Expected response format:
        {
            "success": True,
            "result": {
                "nodes": [{"name": ..., "type": ..., "location": ..., "properties": ...}],
                "links": [{"from_node": ..., "from_socket": ..., "to_node": ..., "to_socket": ...}]
            }
        }
        """
        # Arrange: Set up mock response with nodes and links
        mock_response = {
            "nodes": [
                {
                    "name": "Material Output",
                    "type": "OUTPUT_MATERIAL",
                    "location": [300.0, 100.0],
                    "properties": {},
                },
                {
                    "name": "Principled BSDF",
                    "type": "BSDF_PRINCIPLED",
                    "location": [0.0, 0.0],
                    "properties": {
                        "Base Color": [0.8, 0.8, 0.8, 1.0],
                        "Metallic": 0.0,
                        "Roughness": 0.5,
                    },
                },
                {
                    "name": "Image Texture",
                    "type": "TEX_IMAGE",
                    "location": [-300.0, 0.0],
                    "properties": {"image": "my_texture.png"},
                },
            ],
            "links": [
                {
                    "from_node": "Principled BSDF",
                    "from_socket": "BSDF",
                    "to_node": "Material Output",
                    "to_socket": "Surface",
                },
                {
                    "from_node": "Image Texture",
                    "from_socket": "Color",
                    "to_node": "Principled BSDF",
                    "to_socket": "Base Color",
                },
            ],
        }
        mock_blender_connection.send_command.return_value = mock_response

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_node_tree

            # Act: Call the tool
            result = get_node_tree(mock_context, material_name="MyMaterial")

            # Assert: Verify the response structure
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "result" in result_dict

            # Verify nodes
            assert "nodes" in result_dict["result"]
            nodes = result_dict["result"]["nodes"]
            assert len(nodes) == 3

            # Check first node (Material Output)
            assert nodes[0]["name"] == "Material Output"
            assert nodes[0]["type"] == "OUTPUT_MATERIAL"
            assert nodes[0]["location"] == [300.0, 100.0]

            # Check node with properties
            principled = nodes[1]
            assert principled["name"] == "Principled BSDF"
            assert "properties" in principled
            assert "Base Color" in principled["properties"]

            # Verify links
            assert "links" in result_dict["result"]
            links = result_dict["result"]["links"]
            assert len(links) == 2

            # Check link structure
            assert links[0]["from_node"] == "Principled BSDF"
            assert links[0]["from_socket"] == "BSDF"
            assert links[0]["to_node"] == "Material Output"
            assert links[0]["to_socket"] == "Surface"

            # Verify send_command was called with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "get_node_tree", {"material_name": "MyMaterial"}
            )

    def test_get_node_tree_handles_missing_material(
        self, mock_context, mock_blender_connection
    ):
        """
        Test that get_node_tree returns an error when the material is not found.

        Expected error response:
        {
            "success": False,
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Material 'NonExistent' not found"
            }
        }
        """
        # Arrange: Mock Blender to return an error for missing material
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "NODE_NOT_FOUND",
                "message": "Material 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_node_tree

            # Act: Call the tool
            result = get_node_tree(mock_context, material_name="NonExistent")

            # Assert: Verify error response
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert "error" in result_dict
            assert result_dict["error"]["code"] == "NODE_NOT_FOUND"

    def test_get_node_tree_empty_node_tree(self, mock_context, mock_blender_connection):
        """
        Test that get_node_tree handles a material with no nodes gracefully.
        """
        # Arrange: Set up mock response with empty nodes and links
        mock_response = {"nodes": [], "links": []}
        mock_blender_connection.send_command.return_value = mock_response

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_node_tree

            # Act: Call the tool
            result = get_node_tree(mock_context, material_name="EmptyMaterial")

            # Assert: Verify the response structure
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "result" in result_dict
            assert result_dict["result"]["nodes"] == []
            assert result_dict["result"]["links"] == []

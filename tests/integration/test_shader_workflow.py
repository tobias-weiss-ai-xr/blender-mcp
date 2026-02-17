"""
Integration tests for shader node workflows.

This module tests realistic multi-step shader workflows including:
- Full material creation workflow
- Texture mapping workflow
- Material assignment to objects
"""

import json
import pytest
from unittest.mock import patch, MagicMock


class TestShaderWorkflow:
    """Integration tests for complete shader workflows."""

    def test_full_material_creation_workflow(
        self, mock_context, mock_blender_connection
    ):
        """
        Test the complete material creation workflow:
        1. Create a new material with nodes
        2. Create shader nodes (BSDF, Texture, Output)
        3. Link nodes together
        4. Set node properties
        5. Assign material to an object

        This simulates a realistic user workflow for creating a textured material.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            # Import all needed tools
            from blender_mcp.server import (
                create_material,
                create_shader_node,
                link_shader_nodes,
                set_node_property,
                assign_material,
            )

            # Step 1: Create material with nodes
            mock_blender_connection.send_command.return_value = {
                "name": "MyMaterial",
                "has_nodes": True,
            }
            result = create_material(ctx=mock_context, name="MyMaterial")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "MyMaterial"

            # Step 2: Create an Image Texture node
            mock_blender_connection.send_command.return_value = {
                "name": "Image Texture",
                "type": "TEX_IMAGE",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="MyMaterial",
                node_type="TEX_IMAGE",
                location=[-400, 0],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["type"] == "TEX_IMAGE"

            # Step 3: Create a Principled BSDF node
            mock_blender_connection.send_command.return_value = {
                "name": "Principled BSDF",
                "type": "BSDF_PRINCIPLED",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="MyMaterial",
                node_type="BSDF_PRINCIPLED",
                location=[0, 0],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 4: Link Image Texture Color output to BSDF Base Color
            mock_blender_connection.send_command.return_value = {"linked": True}
            result = link_shader_nodes(
                ctx=mock_context,
                material_name="MyMaterial",
                from_node="Image Texture",
                from_socket="Color",
                to_node="Principled BSDF",
                to_socket="Base Color",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["linked"] is True

            # Step 5: Set BSDF metallic property
            mock_blender_connection.send_command.return_value = {
                "property": "Metallic",
                "value": 0.5,
                "material_name": "MyMaterial",
                "node_name": "Principled BSDF",
            }
            result = set_node_property(
                ctx=mock_context,
                material_name="MyMaterial",
                node_name="Principled BSDF",
                property="Metallic",
                value=0.5,
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["value"] == 0.5

            # Step 6: Assign material to object
            mock_blender_connection.send_command.return_value = {
                "object": "Cube",
                "material": "MyMaterial",
                "slot": 0,
            }
            result = assign_material(
                ctx=mock_context,
                object_name="Cube",
                material_name="MyMaterial",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["object"] == "Cube"

    def test_texture_mapping_workflow(self, mock_context, mock_blender_connection):
        """
        Test texture mapping workflow with coordinates and mapping nodes:
        1. Create material
        2. Add Texture Coordinate node
        3. Add Mapping node
        4. Add Image Texture node
        5. Link the chain: TexCoord -> Mapping -> ImageTexture -> BSDF -> Output
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import (
                create_material,
                create_shader_node,
                link_shader_nodes,
            )

            # Step 1: Create material
            mock_blender_connection.send_command.return_value = {
                "name": "TexturedMaterial",
                "has_nodes": True,
            }
            result = create_material(ctx=mock_context, name="TexturedMaterial")
            assert json.loads(result)["success"] is True

            # Step 2: Create Texture Coordinate node
            mock_blender_connection.send_command.return_value = {
                "name": "Texture Coordinate",
                "type": "TEX_COORD",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="TexturedMaterial",
                node_type="TEX_COORD",
                location=[-800, 0],
            )
            assert json.loads(result)["success"] is True

            # Step 3: Create Mapping node
            mock_blender_connection.send_command.return_value = {
                "name": "Mapping",
                "type": "MAPPING",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="TexturedMaterial",
                node_type="MAPPING",
                location=[-600, 0],
            )
            assert json.loads(result)["success"] is True

            # Step 4: Create Image Texture node
            mock_blender_connection.send_command.return_value = {
                "name": "Image Texture",
                "type": "TEX_IMAGE",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="TexturedMaterial",
                node_type="TEX_IMAGE",
                location=[-400, 0],
            )
            assert json.loads(result)["success"] is True

            # Step 5: Create BSDF node
            mock_blender_connection.send_command.return_value = {
                "name": "Principled BSDF",
                "type": "BSDF_PRINCIPLED",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="TexturedMaterial",
                node_type="BSDF_PRINCIPLED",
                location=[0, 0],
            )
            assert json.loads(result)["success"] is True

            # Step 6: Create Material Output node
            mock_blender_connection.send_command.return_value = {
                "name": "Material Output",
                "type": "OUTPUT_MATERIAL",
            }
            result = create_shader_node(
                ctx=mock_context,
                material_name="TexturedMaterial",
                node_type="OUTPUT_MATERIAL",
                location=[300, 0],
            )
            assert json.loads(result)["success"] is True

            # Step 7-10: Link the chain
            links = [
                ("Texture Coordinate", "UV", "Mapping", "Vector"),
                ("Mapping", "Vector", "Image Texture", "Vector"),
                ("Image Texture", "Color", "Principled BSDF", "Base Color"),
                ("Principled BSDF", "BSDF", "Material Output", "Surface"),
            ]

            for from_node, from_socket, to_node, to_socket in links:
                mock_blender_connection.send_command.return_value = {"linked": True}
                result = link_shader_nodes(
                    ctx=mock_context,
                    material_name="TexturedMaterial",
                    from_node=from_node,
                    from_socket=from_socket,
                    to_node=to_node,
                    to_socket=to_socket,
                )
                assert json.loads(result)["success"] is True

    def test_list_and_get_node_tree_workflow(
        self, mock_context, mock_blender_connection
    ):
        """
        Test the workflow of listing materials and inspecting node trees:
        1. List all materials
        2. Get node tree for a specific material
        3. Verify the structure
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import list_materials, get_node_tree

            # Step 1: List materials
            mock_blender_connection.send_command.return_value = {
                "materials": [
                    {"name": "Material", "use_nodes": True, "users": 1},
                    {"name": "MyCustomMat", "use_nodes": True, "users": 2},
                ]
            }
            result = list_materials(ctx=mock_context)
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            materials = result_dict["result"]["materials"]
            assert len(materials) == 2

            # Step 2: Get node tree for MyCustomMat
            mock_blender_connection.send_command.return_value = {
                "nodes": [
                    {
                        "name": "Material Output",
                        "type": "OUTPUT_MATERIAL",
                        "location": [300, 0],
                    },
                    {
                        "name": "Principled BSDF",
                        "type": "BSDF_PRINCIPLED",
                        "location": [0, 0],
                    },
                ],
                "links": [
                    {
                        "from_node": "Principled BSDF",
                        "from_socket": "BSDF",
                        "to_node": "Material Output",
                        "to_socket": "Surface",
                    }
                ],
            }
            result = get_node_tree(ctx=mock_context, material_name="MyCustomMat")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "nodes" in result_dict["result"]
            assert "links" in result_dict["result"]
            assert len(result_dict["result"]["nodes"]) == 2
            assert len(result_dict["result"]["links"]) == 1


class TestMaterialDeletionWorkflow:
    """Integration tests for material deletion and cleanup workflows."""

    def test_delete_material_workflow(self, mock_context, mock_blender_connection):
        """
        Test the workflow of deleting a material:
        1. List materials to find the one to delete
        2. Delete the material
        3. Verify it's gone by listing again
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import list_materials, delete_material

            # Step 1: List materials
            mock_blender_connection.send_command.return_value = {
                "materials": [
                    {"name": "KeepMe", "use_nodes": True, "users": 1},
                    {"name": "DeleteMe", "use_nodes": True, "users": 0},
                ]
            }
            result = list_materials(ctx=mock_context)
            materials = json.loads(result)["result"]["materials"]
            assert len(materials) == 2

            # Step 2: Delete DeleteMe material
            mock_blender_connection.send_command.return_value = {"deleted": "DeleteMe"}
            result = delete_material(ctx=mock_context, material_name="DeleteMe")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["deleted"] == "DeleteMe"

            # Step 3: List again to verify
            mock_blender_connection.send_command.return_value = {
                "materials": [
                    {"name": "KeepMe", "use_nodes": True, "users": 1},
                ]
            }
            result = list_materials(ctx=mock_context)
            materials = json.loads(result)["result"]["materials"]
            assert len(materials) == 1
            assert materials[0]["name"] == "KeepMe"

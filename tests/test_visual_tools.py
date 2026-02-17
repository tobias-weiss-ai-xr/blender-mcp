"""
Tests for visual verification MCP tools.

This module tests visual verification operations including:
- capture_multi_view_screenshots: Capture screenshots from multiple angles
- export_screenshot_to_file: Export screenshot to file for external analysis
- get_scene_analysis: Get detailed analysis of scene for verification
- verify_geometry: Verify geometry quality for 3D printing

Note: These tools use execute_code internally to run Python in Blender.
"""

import json
import pytest
from unittest.mock import MagicMock, patch


class TestCaptureMultiViewScreenshots:
    """Tests for the capture_multi_view_screenshots MCP tool."""

    def test_capture_multi_view_success(self, mock_context, mock_blender_connection):
        """
        Test successful capture of multi-view screenshots.

        The tool should:
        1. Send an execute_code command to Blender
        2. Return a success response with views and base64 images
        """
        # Arrange: Mock Blender to return success with base64 images
        mock_blender_connection.send_command.return_value = {
            "result": {
                "views": {
                    "top": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "front": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "side": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                    "perspective": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                }
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import capture_multi_view_screenshots

            # Act: Call the tool
            result = capture_multi_view_screenshots(
                ctx=mock_context, views="top,front,side,perspective", resolution=800
            )

            # Assert: Verify execute_code was called
            mock_blender_connection.send_command.assert_called_once()
            call_args = mock_blender_connection.send_command.call_args
            assert call_args[0][0] == "execute_code"
            assert "code" in call_args[0][1]
            # Verify the code contains our parameters
            code = call_args[0][1]["code"]
            assert "top,front,side,perspective" in code
            assert "800" in code

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "views" in result_dict
            assert len(result_dict["views"]) == 4
            assert "top" in result_dict["views"]

    def test_capture_multi_view_invalid_view(
        self, mock_context, mock_blender_connection
    ):
        """
        Test capture with invalid view name.

        The tool should return a valid response but the view won't be captured.
        """
        # Arrange: Mock Blender to return empty views (invalid views not captured)
        mock_blender_connection.send_command.return_value = {
            "result": {
                "views": {}  # Invalid view not captured
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import capture_multi_view_screenshots

            # Act
            result = capture_multi_view_screenshots(
                ctx=mock_context, views="invalid_view", resolution=800
            )

            # Assert: Tool returns success but empty views
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["views"] == {}

    def test_capture_multi_view_error(self, mock_context, mock_blender_connection):
        """
        Test capture when Blender returns an error.
        """
        # Arrange: Mock Blender to return error
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "EXECUTION_ERROR",
                "message": "Failed to capture screenshot",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import capture_multi_view_screenshots

            # Act
            result = capture_multi_view_screenshots(
                ctx=mock_context, views="top", resolution=800
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert "error" in result_dict


class TestExportScreenshotToFile:
    """Tests for the export_screenshot_to_file MCP tool."""

    def test_export_screenshot_success(self, mock_context, mock_blender_connection):
        """
        Test successful export of screenshot to file.

        The tool should:
        1. Send an execute_code command to Blender
        2. Return a success response with filepath and message
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "result": {
                "success": True,
                "filepath": "/tmp/blender_screenshot.png",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import export_screenshot_to_file

            # Act: Call the tool
            result = export_screenshot_to_file(
                ctx=mock_context,
                filepath="/tmp/blender_screenshot.png",
                view="perspective",
                resolution=1024,
            )

            # Assert: Verify execute_code was called
            mock_blender_connection.send_command.assert_called_once()
            call_args = mock_blender_connection.send_command.call_args
            assert call_args[0][0] == "execute_code"
            assert "code" in call_args[0][1]
            # Verify the code contains our parameters
            code = call_args[0][1]["code"]
            assert "/tmp/blender_screenshot.png" in code
            assert "perspective" in code

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["filepath"] == "/tmp/blender_screenshot.png"
            assert "look_at" in result_dict["message"]

    def test_export_screenshot_invalid_path(
        self, mock_context, mock_blender_connection
    ):
        """
        Test export with invalid filepath.

        The tool should return an error when the filepath cannot be written.
        """
        # Arrange: Mock Blender to return error for invalid path
        mock_blender_connection.send_command.return_value = {
            "result": {"error": "Cannot write to path: permission denied"}
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import export_screenshot_to_file

            # Act
            result = export_screenshot_to_file(
                ctx=mock_context,
                filepath="/root/screenshot.png",
                view="perspective",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert "error" in result_dict

    def test_export_screenshot_adds_png_extension(
        self, mock_context, mock_blender_connection
    ):
        """
        Test that .png extension is added if missing.
        """
        mock_blender_connection.send_command.return_value = {
            "result": {
                "success": True,
                "filepath": "/tmp/test.png",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import export_screenshot_to_file

            # Act: Call without .png extension
            result = export_screenshot_to_file(
                ctx=mock_context,
                filepath="/tmp/test",  # No .png extension
                view="top",
            )

            # Assert: .png was added to code
            call_args = mock_blender_connection.send_command.call_args
            code = call_args[0][1]["code"]
            assert "/tmp/test.png" in code


class TestGetSceneAnalysis:
    """Tests for the get_scene_analysis MCP tool."""

    def test_get_scene_analysis_success(self, mock_context, mock_blender_connection):
        """
        Test successful scene analysis.

        The tool should:
        1. Send an execute_code command to Blender
        2. Return a success response with object data and potential issues
        """
        # Arrange: Mock Blender to return analysis data
        mock_blender_connection.send_command.return_value = {
            "result": {
                "object_count": 2,
                "mesh_count": 2,
                "light_count": 1,
                "camera_count": 1,
                "objects": [
                    {
                        "name": "Cube",
                        "type": "MESH",
                        "location": [0.0, 0.0, 0.0],
                    },
                    {
                        "name": "Sphere",
                        "type": "MESH",
                        "location": [3.0, 0.0, 0.0],
                    },
                ],
                "issues": [],
                "bounds": {"min": [-1.0, -1.0, -1.0], "max": [4.0, 1.0, 1.0]},
                "summary": {
                    "total_objects": 2,
                    "meshes": 2,
                    "lights": 1,
                    "cameras": 1,
                    "issues_found": 0,
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_scene_analysis

            # Act: Call the tool
            result = get_scene_analysis(ctx=mock_context)

            # Assert: Verify execute_code was called
            mock_blender_connection.send_command.assert_called_once()
            call_args = mock_blender_connection.send_command.call_args
            assert call_args[0][0] == "execute_code"

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "analysis" in result_dict
            assert result_dict["analysis"]["object_count"] == 2
            assert "objects" in result_dict["analysis"]
            assert len(result_dict["analysis"]["objects"]) == 2

    def test_get_scene_analysis_with_collection(
        self, mock_context, mock_blender_connection
    ):
        """
        Test scene analysis for a specific collection.

        The tool should pass collection_name parameter correctly in the code.
        """
        # Arrange: Mock Blender to return analysis for specific collection
        mock_blender_connection.send_command.return_value = {
            "result": {
                "object_count": 1,
                "mesh_count": 1,
                "light_count": 0,
                "camera_count": 0,
                "objects": [
                    {
                        "name": "Character",
                        "type": "MESH",
                        "location": [0.0, 0.0, 0.0],
                    }
                ],
                "issues": [],
                "summary": {
                    "total_objects": 1,
                    "meshes": 1,
                    "lights": 0,
                    "cameras": 0,
                    "issues_found": 0,
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_scene_analysis

            # Act
            result = get_scene_analysis(ctx=mock_context, collection_name="MyModels")

            # Assert: Verify collection_name was passed in code
            call_args = mock_blender_connection.send_command.call_args
            code = call_args[0][1]["code"]
            assert "MyModels" in code

            # Assert: Verify response
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["analysis"]["object_count"] == 1

    def test_get_scene_analysis_with_floating_objects(
        self, mock_context, mock_blender_connection
    ):
        """
        Test scene analysis detects floating objects.
        """
        # Arrange: Mock Blender to return analysis with issues
        mock_blender_connection.send_command.return_value = {
            "result": {
                "object_count": 1,
                "mesh_count": 1,
                "light_count": 0,
                "camera_count": 0,
                "objects": [
                    {
                        "name": "FloatingCube",
                        "type": "MESH",
                        "location": [0.0, 0.0, 5.0],
                    }
                ],
                "issues": [
                    {
                        "object": "FloatingCube",
                        "type": "floating_object",
                        "message": "Object appears to be floating (z=5.00)",
                    }
                ],
                "summary": {
                    "total_objects": 1,
                    "meshes": 1,
                    "issues_found": 1,
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_scene_analysis

            # Act
            result = get_scene_analysis(ctx=mock_context)

            # Assert: Issue detected
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert len(result_dict["analysis"]["issues"]) == 1
            assert result_dict["analysis"]["issues"][0]["type"] == "floating_object"


class TestVerifyGeometry:
    """Tests for the verify_geometry MCP tool."""

    def test_verify_geometry_success(self, mock_context, mock_blender_connection):
        """
        Test successful geometry verification.

        The tool should:
        1. Send an execute_code command to Blender
        2. Return a success response with check results
        """
        # Arrange: Mock Blender to return verification results
        mock_blender_connection.send_command.return_value = {
            "result": {
                "objects_checked": ["Cube", "Sphere"],
                "checks_performed": ["manifold", "normals", "degenerate"],
                "all_printable": True,
                "results": {
                    "Cube": {
                        "vertex_count": 8,
                        "face_count": 6,
                        "checks": {
                            "manifold": {"is_manifold": True, "non_manifold_edges": 0},
                            "normals": {"consistent": True, "flipped": 0},
                            "degenerate": {"degenerate_faces": 0},
                        },
                        "issues": [],
                        "is_printable": True,
                    },
                    "Sphere": {
                        "vertex_count": 482,
                        "face_count": 960,
                        "checks": {
                            "manifold": {"is_manifold": True, "non_manifold_edges": 0},
                            "normals": {"consistent": True, "flipped": 0},
                            "degenerate": {"degenerate_faces": 0},
                        },
                        "issues": [],
                        "is_printable": True,
                    },
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import verify_geometry

            # Act: Call the tool
            result = verify_geometry(
                ctx=mock_context,
                object_name="",
                checks="manifold,normals,degenerate",
            )

            # Assert: Verify execute_code was called
            mock_blender_connection.send_command.assert_called_once()
            call_args = mock_blender_connection.send_command.call_args
            assert call_args[0][0] == "execute_code"

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "verification" in result_dict
            assert result_dict["verification"]["all_printable"] is True
            assert len(result_dict["verification"]["objects_checked"]) == 2

    def test_verify_geometry_no_issues(self, mock_context, mock_blender_connection):
        """
        Test geometry verification when no issues are found.

        The tool should return printable=True when all checks pass.
        """
        # Arrange
        mock_blender_connection.send_command.return_value = {
            "result": {
                "objects_checked": ["Cube"],
                "checks_performed": ["manifold", "normals"],
                "all_printable": True,
                "results": {
                    "Cube": {
                        "vertex_count": 8,
                        "face_count": 6,
                        "checks": {
                            "manifold": {"is_manifold": True},
                            "normals": {"consistent": True},
                        },
                        "issues": [],
                        "is_printable": True,
                    }
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import verify_geometry

            # Act
            result = verify_geometry(
                ctx=mock_context, object_name="Cube", checks="manifold,normals"
            )

            # Assert
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["verification"]["all_printable"] is True

    def test_verify_geometry_with_issues(self, mock_context, mock_blender_connection):
        """
        Test geometry verification when issues are found.

        The tool should return all_printable=False and list all issues.
        """
        # Arrange: Mock Blender to return issues
        mock_blender_connection.send_command.return_value = {
            "result": {
                "objects_checked": ["BadMesh"],
                "checks_performed": ["manifold", "normals", "degenerate"],
                "all_printable": False,
                "results": {
                    "BadMesh": {
                        "vertex_count": 100,
                        "face_count": 50,
                        "checks": {
                            "manifold": {
                                "is_manifold": False,
                                "non_manifold_edges": 5,
                            },
                            "normals": {
                                "consistent": False,
                                "flipped": 12,
                            },
                            "degenerate": {
                                "degenerate_faces": 3,
                            },
                        },
                        "issues": [
                            {
                                "type": "non_manifold",
                                "count": 5,
                                "message": "Found 5 non-manifold edges",
                            },
                            {
                                "type": "flipped_normals",
                                "count": 12,
                                "message": "Found 12 faces with flipped normals",
                            },
                            {
                                "type": "degenerate_faces",
                                "count": 3,
                                "message": "Found 3 degenerate faces",
                            },
                        ],
                        "is_printable": False,
                    }
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import verify_geometry

            # Act
            result = verify_geometry(
                ctx=mock_context,
                object_name="BadMesh",
                checks="manifold,normals,degenerate",
            )

            # Assert
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["verification"]["all_printable"] is False

            # Verify issue structure
            bad_mesh_result = result_dict["verification"]["results"]["BadMesh"]
            assert len(bad_mesh_result["issues"]) == 3

            issue_types = [issue["type"] for issue in bad_mesh_result["issues"]]
            assert "non_manifold" in issue_types
            assert "flipped_normals" in issue_types
            assert "degenerate_faces" in issue_types

    def test_verify_geometry_specific_object(
        self, mock_context, mock_blender_connection
    ):
        """
        Test geometry verification for a specific object.
        """
        mock_blender_connection.send_command.return_value = {
            "result": {
                "objects_checked": ["Cube"],
                "checks_performed": ["manifold"],
                "all_printable": True,
                "results": {
                    "Cube": {
                        "vertex_count": 8,
                        "face_count": 6,
                        "checks": {
                            "manifold": {"is_manifold": True},
                        },
                        "issues": [],
                        "is_printable": True,
                    }
                },
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import verify_geometry

            # Act
            result = verify_geometry(
                ctx=mock_context,
                object_name="Cube",
                checks="manifold",
            )

            # Assert: object_name passed in code
            call_args = mock_blender_connection.send_command.call_args
            code = call_args[0][1]["code"]
            assert "Cube" in code
            assert "manifold" in code

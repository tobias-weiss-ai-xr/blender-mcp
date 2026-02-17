"""
Tests for animation MCP tools.

This module tests animation operations including:
- set_keyframe: Insert keyframes for object properties
- delete_keyframe: Delete keyframes from object properties
"""

import json
import pytest
from unittest.mock import MagicMock, patch


class TestSetKeyframe:
    """Tests for the set_keyframe MCP tool."""

    def test_set_keyframe_location(self, mock_context, mock_blender_connection):
        """
        Test setting a keyframe for object location.

        The tool should:
        1. Send a set_keyframe command to Blender
        2. Return a success response with object, property, frame, and value
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "object": "Cube",
            "property": "location",
            "frame": 1,
            "value": [1.0, 2.0, 3.0],
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act: Call the tool
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
                frame=1,
                value=[1.0, 2.0, 3.0],
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "set_keyframe",
                {
                    "object_name": "Cube",
                    "property_path": "location",
                    "frame": 1,
                    "value": [1.0, 2.0, 3.0],
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["object"] == "Cube"
            assert result_dict["result"]["property"] == "location"
            assert result_dict["result"]["frame"] == 1
            assert result_dict["result"]["value"] == [1.0, 2.0, 3.0]

    def test_set_keyframe_rotation_euler(self, mock_context, mock_blender_connection):
        """
        Test setting a keyframe for object rotation_euler.

        The tool should handle rotation_euler (XYZ Euler angles in radians).
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "object": "Sphere",
            "property": "rotation_euler",
            "frame": 10,
            "value": [0.0, 0.0, 1.5708],
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act
            result = set_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="rotation_euler",
                frame=10,
                value=[0.0, 0.0, 1.5708],
            )

            # Assert: Verify command was sent
            mock_blender_connection.send_command.assert_called_once_with(
                "set_keyframe",
                {
                    "object_name": "Sphere",
                    "property_path": "rotation_euler",
                    "frame": 10,
                    "value": [0.0, 0.0, 1.5708],
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["property"] == "rotation_euler"

    def test_set_keyframe_scale(self, mock_context, mock_blender_connection):
        """
        Test setting a keyframe for object scale.

        The tool should handle scale as a 3-element array.
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "object": "Cube",
            "property": "scale",
            "frame": 24,
            "value": [2.0, 2.0, 2.0],
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="scale",
                frame=24,
                value=[2.0, 2.0, 2.0],
            )

            # Assert
            mock_blender_connection.send_command.assert_called_once_with(
                "set_keyframe",
                {
                    "object_name": "Cube",
                    "property_path": "scale",
                    "frame": 24,
                    "value": [2.0, 2.0, 2.0],
                },
            )

            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["property"] == "scale"
            assert result_dict["result"]["value"] == [2.0, 2.0, 2.0]

    def test_set_keyframe_individual_component(
        self, mock_context, mock_blender_connection
    ):
        """
        Test setting a keyframe for an individual array component (e.g., location[0]).

        The tool should support indexing into array properties.
        """
        # Arrange: Mock Blender to return success for single component
        mock_blender_connection.send_command.return_value = {
            "object": "Cube",
            "property": "location[0]",
            "frame": 1,
            "value": 5.0,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act: Set just the X component of location
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location[0]",
                frame=1,
                value=5.0,
            )

            # Assert
            mock_blender_connection.send_command.assert_called_once_with(
                "set_keyframe",
                {
                    "object_name": "Cube",
                    "property_path": "location[0]",
                    "frame": 1,
                    "value": 5.0,
                },
            )

            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["property"] == "location[0]"
            assert result_dict["result"]["value"] == 5.0

    def test_set_keyframe_object_not_found(self, mock_context, mock_blender_connection):
        """
        Test error handling when object doesn't exist.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act
            result = set_keyframe(
                ctx=mock_context,
                object_name="NonExistent",
                property_path="location",
                frame=1,
                value=[0.0, 0.0, 0.0],
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"

    def test_set_keyframe_invalid_property(self, mock_context, mock_blender_connection):
        """
        Test error handling when property path is invalid.

        The tool should return an error for invalid property paths.
        """
        # Arrange: Mock Blender to return an error for invalid property
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "INVALID_PROPERTY",
                "message": "Property 'invalid_prop' not found on object 'Cube'",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_keyframe

            # Act
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="invalid_prop",
                frame=1,
                value=1.0,
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "INVALID_PROPERTY"


class TestGetAnimationInfo:
    """Tests for the get_animation_info MCP tool."""

    def test_get_animation_info_animated_object(
        self, mock_context, mock_blender_connection
    ):
        """
        Test getting animation info for an animated object.

        The tool should:
        1. Send a get_animation_info command to Blender
        2. Return a success response with animated_properties, keyframe_count, and frame_range
        """
        # Arrange: Mock Blender to return animation info
        mock_blender_connection.send_command.return_value = {
            "animated_properties": ["location", "rotation_euler"],
            "keyframe_count": 6,
            "frame_range": [1, 24],
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_animation_info

            # Act: Call the tool
            result = get_animation_info(ctx=mock_context, object_name="Cube")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "get_animation_info", {"object_name": "Cube"}
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["animated_properties"] == [
                "location",
                "rotation_euler",
            ]
            assert result_dict["result"]["keyframe_count"] == 6
            assert result_dict["result"]["frame_range"] == [1, 24]

    def test_get_animation_info_non_animated_object(
        self, mock_context, mock_blender_connection
    ):
        """
        Test getting animation info for an object without animation.

        The tool should return empty animated_properties and zero keyframe_count.
        """
        # Arrange: Mock Blender to return empty animation info
        mock_blender_connection.send_command.return_value = {
            "animated_properties": [],
            "keyframe_count": 0,
            "frame_range": None,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_animation_info

            # Act
            result = get_animation_info(ctx=mock_context, object_name="Sphere")

            # Assert
            mock_blender_connection.send_command.assert_called_once_with(
                "get_animation_info", {"object_name": "Sphere"}
            )

            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["animated_properties"] == []
            assert result_dict["result"]["keyframe_count"] == 0
            assert result_dict["result"]["frame_range"] is None

    def test_get_animation_info_object_not_found(
        self, mock_context, mock_blender_connection
    ):
        """
        Test error handling when object doesn't exist.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_animation_info

            # Act
            result = get_animation_info(ctx=mock_context, object_name="NonExistent")

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"


class TestGetNLATracks:
    """Tests for the get_nla_tracks MCP tool."""

    def test_get_nla_tracks_with_tracks(self, mock_context, mock_blender_connection):
        """
        Test getting NLA tracks for an object that has tracks.

        The tool should:
        1. Send a get_nla_tracks command to Blender
        2. Return a success response with tracks list containing name and strips (name, frame_start, frame_end)
        """
        # Arrange: Mock Blender to return NLA tracks
        mock_blender_connection.send_command.return_value = {
            "tracks": [
                {
                    "name": "Walk",
                    "strips": [
                        {"name": "walk_cycle", "frame_start": 1, "frame_end": 24},
                        {"name": "walk_variant", "frame_start": 25, "frame_end": 48},
                    ],
                },
                {
                    "name": "Run",
                    "strips": [
                        {"name": "run_cycle", "frame_start": 1, "frame_end": 12},
                    ],
                },
            ]
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_nla_tracks

            # Act: Call the tool
            result = get_nla_tracks(ctx=mock_context, object_name="Armature")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "get_nla_tracks", {"object_name": "Armature"}
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "tracks" in result_dict["result"]
            assert len(result_dict["result"]["tracks"]) == 2

            # Check first track
            track1 = result_dict["result"]["tracks"][0]
            assert track1["name"] == "Walk"
            assert len(track1["strips"]) == 2
            assert track1["strips"][0]["name"] == "walk_cycle"
            assert track1["strips"][0]["frame_start"] == 1
            assert track1["strips"][0]["frame_end"] == 24

            # Check second track
            track2 = result_dict["result"]["tracks"][1]
            assert track2["name"] == "Run"
            assert len(track2["strips"]) == 1

    def test_get_nla_tracks_no_tracks(self, mock_context, mock_blender_connection):
        """
        Test getting NLA tracks for an object without NLA tracks.

        The tool should return an empty tracks list.
        """
        # Arrange: Mock Blender to return empty tracks
        mock_blender_connection.send_command.return_value = {"tracks": []}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_nla_tracks

            # Act
            result = get_nla_tracks(ctx=mock_context, object_name="Cube")

            # Assert
            mock_blender_connection.send_command.assert_called_once_with(
                "get_nla_tracks", {"object_name": "Cube"}
            )

            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["tracks"] == []

    def test_get_nla_tracks_object_not_found(
        self, mock_context, mock_blender_connection
    ):
        """
        Test error handling when object doesn't exist.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_nla_tracks

            # Act
            result = get_nla_tracks(ctx=mock_context, object_name="NonExistent")

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"


class TestDeleteKeyframe:
    """Tests for the delete_keyframe MCP tool."""

    def test_delete_keyframe_success(self, mock_context, mock_blender_connection):
        """
        Test successful deletion of an existing keyframe.

        The tool should:
        1. Send a delete_keyframe command to Blender
        2. Return a success response with deleted=true
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {"deleted": True}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import delete_keyframe

            # Act: Call the tool
            result = delete_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
                frame=1,
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "delete_keyframe",
                {
                    "object_name": "Cube",
                    "property_path": "location",
                    "frame": 1,
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["deleted"] is True

    def test_delete_keyframe_nonexistent_keyframe(
        self, mock_context, mock_blender_connection
    ):
        """
        Test deleting a keyframe that doesn't exist.

        The tool should handle this gracefully and return deleted=false.
        """
        # Arrange: Mock Blender to return deleted=false (no keyframe to delete)
        mock_blender_connection.send_command.return_value = {"deleted": False}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import delete_keyframe

            # Act
            result = delete_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="rotation_euler",
                frame=100,
            )

            # Assert: Verify response
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["deleted"] is False

    def test_delete_keyframe_object_not_found(
        self, mock_context, mock_blender_connection
    ):
        """
        Test deleting a keyframe from a non-existent object.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import delete_keyframe

            # Act
            result = delete_keyframe(
                ctx=mock_context,
                object_name="NonExistent",
                property_path="location",
                frame=1,
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"


class TestTimelineControl:
    """Tests for the timeline_control MCP tool."""

    def test_timeline_control_play(self, mock_context, mock_blender_connection):
        """
        Test timeline play action.

        The tool should:
        1. Send a timeline_control command with action='play' to Blender
        2. Return a success response with action, current_frame, and is_playing
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "action": "play",
            "current_frame": 1,
            "is_playing": True,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Act: Call the tool with play action
            result = timeline_control(ctx=mock_context, action="play")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "timeline_control",
                {"action": "play", "frame": None},
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["action"] == "play"
            assert result_dict["result"]["current_frame"] == 1
            assert result_dict["result"]["is_playing"] is True

    def test_timeline_control_pause(self, mock_context, mock_blender_connection):
        """
        Test timeline pause action.

        The tool should pause playback and return the current state.
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "action": "pause",
            "current_frame": 24,
            "is_playing": False,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Act: Call the tool with pause action
            result = timeline_control(ctx=mock_context, action="pause")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "timeline_control",
                {"action": "pause", "frame": None},
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["action"] == "pause"
            assert result_dict["result"]["is_playing"] is False

    def test_timeline_control_stop(self, mock_context, mock_blender_connection):
        """
        Test timeline stop action.

        The tool should stop playback and return the current state.
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "action": "stop",
            "current_frame": 1,
            "is_playing": False,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Act: Call the tool with stop action
            result = timeline_control(ctx=mock_context, action="stop")

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "timeline_control",
                {"action": "stop", "frame": None},
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["action"] == "stop"
            assert result_dict["result"]["is_playing"] is False

    def test_timeline_control_seek(self, mock_context, mock_blender_connection):
        """
        Test timeline seek action.

        The tool should seek to the specified frame and return the current state.
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "action": "seek",
            "current_frame": 50,
            "is_playing": False,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Act: Call the tool with seek action and frame
            result = timeline_control(ctx=mock_context, action="seek", frame=50)

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "timeline_control",
                {"action": "seek", "frame": 50},
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["action"] == "seek"
            assert result_dict["result"]["current_frame"] == 50
            assert result_dict["result"]["is_playing"] is False

    def test_timeline_control_invalid_action(
        self, mock_context, mock_blender_connection
    ):
        """
        Test timeline_control with invalid action.

        The tool should return an error for invalid actions.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Act: Call with invalid action
            result = timeline_control(ctx=mock_context, action="invalid_action")

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "INVALID_INPUT"


class TestCreateNLATrack:
    """Tests for the create_nla_track MCP tool."""

    def test_create_nla_track(self, mock_context, mock_blender_connection):
        """
        Test creating a new NLA track for an object.

        The tool should:
        1. Send a create_nla_track command to Blender
        2. Return a success response with the track name
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "name": "WalkCycle",
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_nla_track

            # Act: Call the tool
            result = create_nla_track(
                ctx=mock_context,
                object_name="Character",
                track_name="WalkCycle",
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "create_nla_track",
                {
                    "object_name": "Character",
                    "track_name": "WalkCycle",
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "WalkCycle"

    def test_create_nla_track_object_not_found(
        self, mock_context, mock_blender_connection
    ):
        """
        Test error handling when object doesn't exist.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_nla_track

            # Act
            result = create_nla_track(
                ctx=mock_context,
                object_name="NonExistent",
                track_name="MyTrack",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"


class TestSetFrameRange:
    """Tests for the set_frame_range MCP tool."""

    def test_set_frame_range_success(self, mock_context, mock_blender_connection):
        """
        Test setting the frame range successfully.

        The tool should:
        1. Send a set_frame_range command to Blender
        2. Return a success response with start and end frame
        """
        # Arrange: Mock Blender to return success
        mock_blender_connection.send_command.return_value = {
            "start": 1,
            "end": 250,
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import set_frame_range

            # Act: Call the tool
            result = set_frame_range(
                ctx=mock_context,
                start=1,
                end=250,
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "set_frame_range",
                {
                    "start": 1,
                    "end": 250,
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["start"] == 1
            assert result_dict["result"]["end"] == 250


class TestGetFCurveData:
    """Tests for the get_fcurve_data MCP tool."""

    def test_get_fcurve_data_all_fcurves(self, mock_context, mock_blender_connection):
        """
        Test getting all FCurve data for an object.

        The tool should:
        1. Send a get_fcurve_data command to Blender
        2. Return a success response with fcurves list containing data_path and keyframes
        """
        # Arrange: Mock Blender to return FCurve data
        mock_blender_connection.send_command.return_value = {
            "fcurves": [
                {
                    "data_path": "location",
                    "keyframes": [
                        {"frame": 1, "value": 0.0},
                        {"frame": 24, "value": 5.0},
                    ],
                },
                {
                    "data_path": "scale",
                    "keyframes": [
                        {"frame": 1, "value": 1.0},
                        {"frame": 24, "value": 2.0},
                    ],
                },
            ]
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_fcurve_data

            # Act: Call the tool without property_path filter
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="Cube",
            )

            # Assert: Verify command was sent with correct params
            mock_blender_connection.send_command.assert_called_once_with(
                "get_fcurve_data",
                {
                    "object_name": "Cube",
                    "property_path": None,
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert "fcurves" in result_dict["result"]
            assert len(result_dict["result"]["fcurves"]) == 2
            assert result_dict["result"]["fcurves"][0]["data_path"] == "location"
            assert len(result_dict["result"]["fcurves"][0]["keyframes"]) == 2
            assert result_dict["result"]["fcurves"][0]["keyframes"][0]["frame"] == 1
            assert result_dict["result"]["fcurves"][0]["keyframes"][0]["value"] == 0.0

    def test_get_fcurve_data_filter_by_property(
        self, mock_context, mock_blender_connection
    ):
        """
        Test getting FCurve data filtered by property path.

        The tool should filter results to only include matching data_path.
        """
        # Arrange: Mock Blender to return filtered FCurve data
        mock_blender_connection.send_command.return_value = {
            "fcurves": [
                {
                    "data_path": "location",
                    "keyframes": [
                        {"frame": 1, "value": 0.0},
                        {"frame": 24, "value": 5.0},
                    ],
                },
            ]
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_fcurve_data

            # Act: Call the tool with property_path filter
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
            )

            # Assert: Verify command was sent with filter
            mock_blender_connection.send_command.assert_called_once_with(
                "get_fcurve_data",
                {
                    "object_name": "Cube",
                    "property_path": "location",
                },
            )

            # Assert: Verify response format
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert len(result_dict["result"]["fcurves"]) == 1
            assert result_dict["result"]["fcurves"][0]["data_path"] == "location"

    def test_get_fcurve_data_no_animation(self, mock_context, mock_blender_connection):
        """
        Test getting FCurve data for an object without animation.

        The tool should return an empty fcurves list.
        """
        # Arrange: Mock Blender to return empty fcurves
        mock_blender_connection.send_command.return_value = {"fcurves": []}

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_fcurve_data

            # Act
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="Cube",
            )

            # Assert
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["fcurves"] == []

    def test_get_fcurve_data_object_not_found(
        self, mock_context, mock_blender_connection
    ):
        """
        Test error handling when object doesn't exist.

        The tool should return an error when the object is not found.
        """
        # Arrange: Mock Blender to return an error for missing object
        mock_blender_connection.send_command.return_value = {
            "error": {
                "code": "OBJECT_NOT_FOUND",
                "message": "Object 'NonExistent' not found",
            }
        }

        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import get_fcurve_data

            # Act
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="NonExistent",
            )

            # Assert: Error response format
            result_dict = json.loads(result)
            assert result_dict["success"] is False
            assert result_dict["error"]["code"] == "OBJECT_NOT_FOUND"

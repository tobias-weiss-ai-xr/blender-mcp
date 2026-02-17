"""
Integration tests for animation workflows.

This module tests realistic multi-step animation workflows including:
- Full keyframe animation workflow
- Timeline control workflow
- NLA track management workflow
"""

import json
import pytest
from unittest.mock import patch, MagicMock


class TestAnimationWorkflow:
    """Integration tests for complete animation workflows."""

    def test_full_keyframe_animation_workflow(
        self, mock_context, mock_blender_connection
    ):
        """
        Test the complete keyframe animation workflow:
        1. Set frame range for the animation
        2. Set keyframes for object location at multiple frames
        3. Set keyframes for rotation
        4. Get animation info to verify
        5. Get FCurve data to inspect keyframes

        This simulates a realistic user workflow for animating an object.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import (
                set_frame_range,
                set_keyframe,
                get_animation_info,
                get_fcurve_data,
            )

            # Step 1: Set frame range
            mock_blender_connection.send_command.return_value = {
                "start": 1,
                "end": 60,
            }
            result = set_frame_range(ctx=mock_context, start=1, end=60)
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["start"] == 1
            assert result_dict["result"]["end"] == 60

            # Step 2: Set location keyframe at frame 1
            mock_blender_connection.send_command.return_value = {
                "object": "Cube",
                "property": "location",
                "frame": 1,
                "value": [0.0, 0.0, 0.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
                frame=1,
                value=[0.0, 0.0, 0.0],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 3: Set location keyframe at frame 30 (moved right)
            mock_blender_connection.send_command.return_value = {
                "object": "Cube",
                "property": "location",
                "frame": 30,
                "value": [5.0, 0.0, 0.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
                frame=30,
                value=[5.0, 0.0, 0.0],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 4: Set location keyframe at frame 60 (back to start)
            mock_blender_connection.send_command.return_value = {
                "object": "Cube",
                "property": "location",
                "frame": 60,
                "value": [0.0, 0.0, 0.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
                frame=60,
                value=[0.0, 0.0, 0.0],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 5: Set rotation keyframe at frame 30 (90 degree rotation)
            mock_blender_connection.send_command.return_value = {
                "object": "Cube",
                "property": "rotation_euler",
                "frame": 30,
                "value": [0.0, 0.0, 1.5708],  # 90 degrees in radians
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Cube",
                property_path="rotation_euler",
                frame=30,
                value=[0.0, 0.0, 1.5708],
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 6: Get animation info
            mock_blender_connection.send_command.return_value = {
                "animated_properties": ["location", "rotation_euler"],
                "keyframe_count": 4,
                "frame_range": [1, 60],
            }
            result = get_animation_info(ctx=mock_context, object_name="Cube")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["keyframe_count"] == 4
            assert "location" in result_dict["result"]["animated_properties"]

            # Step 7: Get FCurve data for location
            mock_blender_connection.send_command.return_value = {
                "fcurves": [
                    {
                        "data_path": "location",
                        "keyframes": [
                            {"frame": 1, "value": 0.0},
                            {"frame": 30, "value": 5.0},
                            {"frame": 60, "value": 0.0},
                        ],
                    }
                ]
            }
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="Cube",
                property_path="location",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert len(result_dict["result"]["fcurves"]) == 1
            assert len(result_dict["result"]["fcurves"][0]["keyframes"]) == 3

    def test_timeline_playback_workflow(self, mock_context, mock_blender_connection):
        """
        Test the timeline control workflow:
        1. Seek to a specific frame
        2. Start playback
        3. Pause playback
        4. Seek to another frame
        5. Stop playback

        This simulates a user controlling animation playback.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import timeline_control

            # Step 1: Seek to frame 10
            mock_blender_connection.send_command.return_value = {
                "action": "seek",
                "current_frame": 10,
                "is_playing": False,
            }
            result = timeline_control(ctx=mock_context, action="seek", frame=10)
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["current_frame"] == 10
            assert result_dict["result"]["is_playing"] is False

            # Step 2: Start playback
            mock_blender_connection.send_command.return_value = {
                "action": "play",
                "current_frame": 10,
                "is_playing": True,
            }
            result = timeline_control(ctx=mock_context, action="play")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["is_playing"] is True

            # Step 3: Pause playback
            mock_blender_connection.send_command.return_value = {
                "action": "pause",
                "current_frame": 25,
                "is_playing": False,
            }
            result = timeline_control(ctx=mock_context, action="pause")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["is_playing"] is False

            # Step 4: Seek to frame 50
            mock_blender_connection.send_command.return_value = {
                "action": "seek",
                "current_frame": 50,
                "is_playing": False,
            }
            result = timeline_control(ctx=mock_context, action="seek", frame=50)
            result_dict = json.loads(result)
            assert result_dict["result"]["current_frame"] == 50

            # Step 5: Stop playback (returns to frame 1)
            mock_blender_connection.send_command.return_value = {
                "action": "stop",
                "current_frame": 1,
                "is_playing": False,
            }
            result = timeline_control(ctx=mock_context, action="stop")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["current_frame"] == 1


class TestKeyframeEditingWorkflow:
    """Integration tests for editing and deleting keyframes."""

    def test_delete_and_modify_keyframes(self, mock_context, mock_blender_connection):
        """
        Test the workflow of editing keyframes:
        1. Set initial keyframes
        2. Delete a keyframe
        3. Set a new keyframe to replace it
        4. Verify with FCurve data
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import (
                set_keyframe,
                delete_keyframe,
                get_fcurve_data,
            )

            # Step 1: Set initial keyframe
            mock_blender_connection.send_command.return_value = {
                "object": "Sphere",
                "property": "location",
                "frame": 1,
                "value": [0.0, 0.0, 0.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="location",
                frame=1,
                value=[0.0, 0.0, 0.0],
            )
            assert json.loads(result)["success"] is True

            # Step 2: Delete the keyframe
            mock_blender_connection.send_command.return_value = {"deleted": True}
            result = delete_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="location",
                frame=1,
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["deleted"] is True

            # Step 3: Set new keyframe with different value
            mock_blender_connection.send_command.return_value = {
                "object": "Sphere",
                "property": "location",
                "frame": 1,
                "value": [2.0, 2.0, 2.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="location",
                frame=1,
                value=[2.0, 2.0, 2.0],
            )
            assert json.loads(result)["success"] is True

            # Step 4: Verify with FCurve data
            mock_blender_connection.send_command.return_value = {
                "fcurves": [
                    {
                        "data_path": "location",
                        "keyframes": [
                            {"frame": 1, "value": 2.0},
                        ],
                    }
                ]
            }
            result = get_fcurve_data(
                ctx=mock_context,
                object_name="Sphere",
                property_path="location",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["fcurves"][0]["keyframes"][0]["value"] == 2.0


class TestNLATrackWorkflow:
    """Integration tests for NLA (Non-Linear Animation) workflows."""

    def test_nla_track_management_workflow(self, mock_context, mock_blender_connection):
        """
        Test the NLA track workflow:
        1. Create a new NLA track
        2. Get NLA tracks to verify creation
        3. Verify track structure

        This simulates managing complex animation blending through NLA.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import create_nla_track, get_nla_tracks

            # Step 1: Create WalkCycle track
            mock_blender_connection.send_command.return_value = {
                "name": "WalkCycle",
            }
            result = create_nla_track(
                ctx=mock_context,
                object_name="Character",
                track_name="WalkCycle",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            assert result_dict["result"]["name"] == "WalkCycle"

            # Step 2: Create RunCycle track
            mock_blender_connection.send_command.return_value = {
                "name": "RunCycle",
            }
            result = create_nla_track(
                ctx=mock_context,
                object_name="Character",
                track_name="RunCycle",
            )
            result_dict = json.loads(result)
            assert result_dict["success"] is True

            # Step 3: Get all NLA tracks
            mock_blender_connection.send_command.return_value = {
                "tracks": [
                    {
                        "name": "WalkCycle",
                        "strips": [
                            {"name": "walk_action", "frame_start": 1, "frame_end": 24},
                        ],
                    },
                    {
                        "name": "RunCycle",
                        "strips": [
                            {"name": "run_action", "frame_start": 1, "frame_end": 12},
                        ],
                    },
                ]
            }
            result = get_nla_tracks(ctx=mock_context, object_name="Character")
            result_dict = json.loads(result)
            assert result_dict["success"] is True
            tracks = result_dict["result"]["tracks"]
            assert len(tracks) == 2
            assert tracks[0]["name"] == "WalkCycle"
            assert tracks[1]["name"] == "RunCycle"

    def test_complete_animation_scene_workflow(
        self, mock_context, mock_blender_connection
    ):
        """
        Test a complete scene animation workflow:
        1. Set frame range
        2. Animate multiple objects
        3. Create NLA tracks
        4. Verify animation state

        This simulates setting up a complete animated scene.
        """
        with patch(
            "blender_mcp.server.get_blender_connection",
            return_value=mock_blender_connection,
        ):
            from blender_mcp.server import (
                set_frame_range,
                set_keyframe,
                create_nla_track,
                get_nla_tracks,
                get_animation_info,
            )

            # Step 1: Set scene frame range
            mock_blender_connection.send_command.return_value = {
                "start": 1,
                "end": 120,
            }
            result = set_frame_range(ctx=mock_context, start=1, end=120)
            assert json.loads(result)["success"] is True

            # Step 2: Animate Cube - location bouncing
            for frame, z_value in [
                (1, 0.0),
                (30, 2.0),
                (60, 0.0),
                (90, 2.0),
                (120, 0.0),
            ]:
                mock_blender_connection.send_command.return_value = {
                    "object": "Cube",
                    "property": "location",
                    "frame": frame,
                    "value": [0.0, 0.0, z_value],
                }
                result = set_keyframe(
                    ctx=mock_context,
                    object_name="Cube",
                    property_path="location",
                    frame=frame,
                    value=[0.0, 0.0, z_value],
                )
                assert json.loads(result)["success"] is True

            # Step 3: Animate Sphere - rotation
            mock_blender_connection.send_command.return_value = {
                "object": "Sphere",
                "property": "rotation_euler",
                "frame": 1,
                "value": [0.0, 0.0, 0.0],
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="rotation_euler",
                frame=1,
                value=[0.0, 0.0, 0.0],
            )
            assert json.loads(result)["success"] is True

            mock_blender_connection.send_command.return_value = {
                "object": "Sphere",
                "property": "rotation_euler",
                "frame": 120,
                "value": [0.0, 0.0, 6.28],  # 360 degrees
            }
            result = set_keyframe(
                ctx=mock_context,
                object_name="Sphere",
                property_path="rotation_euler",
                frame=120,
                value=[0.0, 0.0, 6.28],
            )
            assert json.loads(result)["success"] is True

            # Step 4: Create NLA track for Character
            mock_blender_connection.send_command.return_value = {"name": "Action"}
            result = create_nla_track(
                ctx=mock_context,
                object_name="Character",
                track_name="Action",
            )
            assert json.loads(result)["success"] is True

            # Step 5: Verify Cube animation info
            mock_blender_connection.send_command.return_value = {
                "animated_properties": ["location"],
                "keyframe_count": 5,
                "frame_range": [1, 120],
            }
            result = get_animation_info(ctx=mock_context, object_name="Cube")
            result_dict = json.loads(result)
            assert result_dict["result"]["keyframe_count"] == 5
            assert result_dict["result"]["frame_range"] == [1, 120]

            # Step 6: Verify Sphere animation info
            mock_blender_connection.send_command.return_value = {
                "animated_properties": ["rotation_euler"],
                "keyframe_count": 2,
                "frame_range": [1, 120],
            }
            result = get_animation_info(ctx=mock_context, object_name="Sphere")
            result_dict = json.loads(result)
            assert result_dict["result"]["keyframe_count"] == 2

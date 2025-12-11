"""
Video transition WebSocket command handler.
Handles video:transition command for creating fade transitions between videos.
"""
import asyncio
from typing import Callable, Any

from services.video_transition import VideoTransitionService

# Singleton service instance
_transition_service = VideoTransitionService()


async def handle_video_transition(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle video:transition WebSocket command.

    Expected data:
        file1_path: str - Relative path to first video
        file2_path: str - Relative path to second video
        output_dir: str (optional) - Output directory
        transition_duration: float (optional) - Crossfade duration (default: 1.0)
        keep_intermediate: bool (optional) - Keep intermediate files (default: true)
        transition_only: bool (optional) - Only create transition, skip joining (default: false)

    Returns:
        dict with initial status acknowledgment
    """
    file1_path = data.get("file1_path")
    file2_path = data.get("file2_path")
    output_dir = data.get("output_dir")
    transition_duration = data.get("transition_duration", 1.0)
    keep_intermediate = data.get("keep_intermediate", True)
    transition_only = data.get("transition_only", False)

    # Validate input
    if not file1_path:
        return {
            "success": False,
            "error": "Missing file1_path"
        }

    if not file2_path:
        return {
            "success": False,
            "error": "Missing file2_path"
        }

    # Validate transition_duration is a positive number
    try:
        transition_duration = float(transition_duration)
        if transition_duration <= 0:
            return {
                "success": False,
                "error": "transition_duration must be positive"
            }
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "transition_duration must be a number"
        }

    # Create async progress callback
    async def progress_callback(event_type: str, event_data: dict):
        message = {
            "command": f"video:{event_type}",
            "sender": "backend",
            "target": "frontend",
            "data": event_data
        }
        await broadcast_callback(message)

    # Run transition in background task
    asyncio.create_task(
        _transition_service.create_transition(
            file1_path,
            file2_path,
            output_dir,
            transition_duration,
            keep_intermediate,
            transition_only,
            progress_callback
        )
    )

    return {
        "success": True,
        "message": f"Transition started: {file1_path} -> {file2_path}",
        "transition_duration": transition_duration,
        "transition_only": transition_only
    }

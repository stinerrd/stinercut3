"""
Video splitter WebSocket command handler.
Handles video:split command for splitting videos at keyframe boundaries.
"""
import asyncio
from typing import Callable, Any

from services.video_splitter import VideoSplitterService

# Singleton service instance
_splitter_service = VideoSplitterService()


async def handle_video_split(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle video:split WebSocket command.

    Expected data:
        input_path: str - Relative path to video (e.g., "input/abc123/video.mp4")
        timestamps: list[float] - Split points in seconds
        output_dir: str (optional) - Output directory

    Returns:
        dict with initial status acknowledgment
    """
    input_path = data.get("input_path")
    timestamps = data.get("timestamps", [])
    output_dir = data.get("output_dir")

    # Validate input
    if not input_path:
        return {
            "success": False,
            "error": "Missing input_path"
        }

    if not timestamps or not isinstance(timestamps, list):
        return {
            "success": False,
            "error": "Missing or invalid timestamps (must be non-empty list)"
        }

    # Validate timestamps are numbers
    try:
        timestamps = [float(t) for t in timestamps]
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "All timestamps must be numbers"
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

    # Run split in background task
    asyncio.create_task(
        _splitter_service.split_video(
            input_path, timestamps, output_dir, progress_callback
        )
    )

    return {
        "success": True,
        "message": f"Split started for {input_path}",
        "timestamps_count": len(timestamps)
    }

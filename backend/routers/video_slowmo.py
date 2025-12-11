"""
Video slow motion WebSocket command handler.
Handles video:slowmo command for converting videos to slow motion.
"""
import asyncio
from typing import Callable, Any

from services.video_slowmo import VideoSlowmoService

# Singleton service instance
_slowmo_service = VideoSlowmoService()


async def handle_video_slowmo(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle video:slowmo WebSocket command.

    Expected data:
        input_path: str - Relative path to video (e.g., "input/abc123/video.mp4")
        speed_factor: float - Speed multiplier (0.1 to 1.0, default 0.5)
        output_dir: str (optional) - Output directory

    Returns:
        dict with initial status acknowledgment
    """
    input_path = data.get("input_path")
    speed_factor = data.get("speed_factor", 0.5)
    output_dir = data.get("output_dir")

    # Validate input
    if not input_path:
        return {
            "success": False,
            "error": "Missing input_path"
        }

    # Validate speed_factor
    try:
        speed_factor = float(speed_factor)
    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "speed_factor must be a number"
        }

    if speed_factor <= 0 or speed_factor > 1.0:
        return {
            "success": False,
            "error": "speed_factor must be between 0.1 and 1.0"
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

    # Run conversion in background task
    asyncio.create_task(
        _slowmo_service.convert_slowmo(
            input_path, speed_factor, output_dir, progress_callback
        )
    )

    return {
        "success": True,
        "message": f"Slowmo conversion started for {input_path}",
        "speed_factor": speed_factor
    }

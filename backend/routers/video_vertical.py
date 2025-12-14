"""
Video vertical WebSocket command handler.
Handles video:vertical command for converting videos to 9:16 format.
"""
import asyncio
from typing import Callable, Any

from services.video_vertical import VideoVerticalService, CropMethod

# Singleton service instance
_vertical_service = VideoVerticalService()


async def handle_video_vertical(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle video:vertical WebSocket command.

    Expected data:
        input_path: str - Relative path to video (e.g., "uploads/video.mp4")
        method: str - "center" or "face_tracking" (default: "center")
        output_size: str - "1080p", "720p", or "native" (default: "1080p")
        output_dir: str (optional) - Output directory
        center_offset: float (optional) - Offset from center as percentage (-50 to +50)
                       Negative = left, Positive = right. Default: 0

    Returns:
        dict with initial status acknowledgment
    """
    input_path = data.get("input_path")
    method_str = data.get("method", "center")
    output_size = data.get("output_size", "1080p")
    output_dir = data.get("output_dir")
    center_offset = data.get("center_offset", 0.0)

    # Validate input
    if not input_path:
        return {
            "success": False,
            "error": "Missing input_path"
        }

    # Parse method
    try:
        method = CropMethod(method_str)
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid method: {method_str}. Use 'center' or 'face_tracking'"
        }

    # Validate output_size
    valid_sizes = ["1080p", "720p", "native"]
    if output_size not in valid_sizes:
        return {
            "success": False,
            "error": f"Invalid output_size: {output_size}. Use '1080p', '720p', or 'native'"
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

    # Validate center_offset
    try:
        center_offset = float(center_offset)
    except (TypeError, ValueError):
        center_offset = 0.0

    # Run conversion in background task
    asyncio.create_task(
        _vertical_service.convert_to_vertical(
            input_path, method, output_size, output_dir, center_offset, progress_callback
        )
    )

    return {
        "success": True,
        "message": f"Vertical conversion started for {input_path}",
        "method": method_str,
        "output_size": output_size,
        "center_offset": center_offset
    }

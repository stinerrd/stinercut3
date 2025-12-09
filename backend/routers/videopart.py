"""
Videopart Router
Handles videopart-related API endpoints and WebSocket message processing.
"""
from fastapi import APIRouter

from database import SessionLocal
from services.videopart_service import VideopartService

router = APIRouter(prefix="/api/videoparts", tags=["videoparts"])

# Singleton service instance
_videopart_service = VideopartService()


async def handle_videopart_uploaded(data: dict) -> dict:
    """
    Handler called from WebSocket hub when 'videopart:uploaded' message is received.

    Expected data format:
    {
        "id": int,          # Videopart ID in database
        "name": str,        # Videopart name
        "type": str,        # 'intro' or 'outro'
        "file_path": str    # Relative path to video file
    }

    Returns:
        dict with processing result to send back to frontend
    """
    videopart_id = data.get("id")
    file_path = data.get("file_path")

    if not videopart_id or not file_path:
        return {
            "success": False,
            "id": videopart_id,
            "error": "Missing required fields: id and file_path"
        }

    # Create database session for this operation
    db = SessionLocal()
    try:
        result = await _videopart_service.process_uploaded(
            videopart_id=videopart_id,
            file_path=file_path,
            db=db
        )
        return result
    finally:
        db.close()

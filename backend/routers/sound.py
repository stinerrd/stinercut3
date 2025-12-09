"""
Sound Router
Handles sound-related WebSocket message processing.
"""
from fastapi import APIRouter

from database import SessionLocal
from services.sound_service import SoundService

router = APIRouter(prefix="/api/sounds", tags=["sounds"])

# Singleton service instance
_sound_service = SoundService()


async def handle_sound_uploaded(data: dict) -> dict:
    """
    Handler called from WebSocket hub when 'sound:uploaded' message is received.

    Expected data format:
    {
        "id": int,          # Sound ID in database
        "name": str,        # Sound name
        "type": str,        # 'boden', 'plane', 'freefall', 'canopy'
        "file_path": str    # Relative path to audio file
    }

    Returns:
        dict with processing result to send back to frontend
    """
    sound_id = data.get("id")
    file_path = data.get("file_path")

    if not sound_id or not file_path:
        return {
            "success": False,
            "id": sound_id,
            "error": "Missing required fields: id and file_path"
        }

    # Create database session for this operation
    db = SessionLocal()
    try:
        result = await _sound_service.process_uploaded(
            sound_id=sound_id,
            file_path=file_path,
            db=db
        )
        return result
    finally:
        db.close()

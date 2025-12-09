"""
Videopart Processing Service
Handles videopart processing after upload: folder creation, duration extraction, thumbnail generation.
"""
import os
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from services.ffmpeg_service import FFmpegService
from models.videopart import Videopart


class VideopartService:
    """Service for processing uploaded videoparts."""

    VIDEODATA_BASE = "/videodata"
    VIDEOPARTS_DIR = "media/videoparts"

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()

    async def process_uploaded(self, videopart_id: int, file_path: str, db: Session) -> dict:
        """
        Process an uploaded videopart:
        1. Validate videopart exists in database
        2. Create folder for future resolution variants
        3. Extract video duration
        4. Generate thumbnail at midpoint
        5. Update database record
        6. Return result data

        Args:
            videopart_id: The ID of the videopart in database
            file_path: Relative path to the video file (e.g., "media/videoparts/intro_xxx.mp4")
            db: SQLAlchemy database session

        Returns:
            dict with success status and processed data
        """
        try:
            # 1. Validate videopart exists
            videopart = db.query(Videopart).filter(Videopart.id == videopart_id).first()
            if not videopart:
                return {
                    "success": False,
                    "id": videopart_id,
                    "error": f"Videopart with ID {videopart_id} not found"
                }

            # 2. Build full path and create folder
            # file_path from DB is just filename, need to prepend videoparts directory
            full_path = os.path.join(self.VIDEODATA_BASE, self.VIDEOPARTS_DIR, file_path)
            if not os.path.exists(full_path):
                return {
                    "success": False,
                    "id": videopart_id,
                    "error": f"Video file not found: {full_path}"
                }

            # Create folder with same name as file (without extension)
            folder_path = os.path.splitext(full_path)[0]
            folder_relative = os.path.join(self.VIDEOPARTS_DIR, os.path.splitext(file_path)[0])

            if not os.path.exists(folder_path):
                os.makedirs(folder_path, mode=0o755)
                print(f"[VideopartService] Created folder: {folder_path}")

            # 3. Extract duration (run in thread to not block async loop)
            duration = await asyncio.to_thread(self.ffmpeg.get_duration, full_path)
            duration_int = int(duration)

            # 4. Generate thumbnail at midpoint
            midpoint = duration / 2
            thumbnail_bytes = await asyncio.to_thread(
                self.ffmpeg.extract_thumbnail_jpeg, full_path, midpoint
            )

            # 5. Update database record
            videopart.duration = duration_int
            videopart.thumbnail = thumbnail_bytes
            videopart.updated_at = datetime.utcnow()
            db.commit()

            print(f"[VideopartService] Processed videopart {videopart_id}: "
                  f"duration={duration_int}s, thumbnail={len(thumbnail_bytes)} bytes")

            # 6. Return success result
            return {
                "success": True,
                "id": videopart_id,
                "duration": duration_int,
                "has_thumbnail": True,
                "folder": folder_relative
            }

        except Exception as e:
            db.rollback()
            print(f"[VideopartService] Error processing videopart {videopart_id}: {e}")
            return {
                "success": False,
                "id": videopart_id,
                "error": str(e)
            }

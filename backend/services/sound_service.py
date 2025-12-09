"""
Sound Processing Service
Handles sound processing after upload: MP3 to WAV conversion, normalization,
duration extraction, and waveform generation.
"""
import os
import asyncio
from datetime import datetime
from sqlalchemy.orm import Session

from services.ffmpeg_service import FFmpegService
from models.sound import Sound


class SoundService:
    """Service for processing uploaded sounds."""

    VIDEODATA_BASE = "/videodata"
    SOUNDS_DIR = "media/sounds"

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()

    async def process_uploaded(self, sound_id: int, file_path: str, db: Session) -> dict:
        """
        Process an uploaded sound:
        1. Validate sound exists in database
        2. If MP3, convert to normalized WAV (replace original)
        3. Extract audio duration
        4. Generate waveform image (1200x200)
        5. Update database record
        6. Return result data

        Args:
            sound_id: The ID of the sound in database
            file_path: Relative filename (e.g., "boden_20251209_xxx.mp3")
            db: SQLAlchemy database session

        Returns:
            dict with success status and processed data
        """
        try:
            # 1. Validate sound exists
            sound = db.query(Sound).filter(Sound.id == sound_id).first()
            if not sound:
                return {
                    "success": False,
                    "id": sound_id,
                    "error": f"Sound with ID {sound_id} not found"
                }

            # 2. Build full path
            full_path = os.path.join(self.VIDEODATA_BASE, self.SOUNDS_DIR, file_path)
            if not os.path.exists(full_path):
                return {
                    "success": False,
                    "id": sound_id,
                    "error": f"Audio file not found: {full_path}"
                }

            # 3. If MP3, convert to normalized WAV (replace original)
            file_ext = os.path.splitext(file_path)[1].lower()
            current_path = full_path
            new_file_path = file_path

            if file_ext == '.mp3':
                # Generate WAV filename
                wav_filename = os.path.splitext(file_path)[0] + '.wav'
                wav_full_path = os.path.join(self.VIDEODATA_BASE, self.SOUNDS_DIR, wav_filename)

                print(f"[SoundService] Converting MP3 to WAV: {file_path} -> {wav_filename}")

                # Convert to normalized WAV (run in thread)
                await asyncio.to_thread(
                    self.ffmpeg.convert_to_wav_normalized, full_path, wav_full_path
                )

                # Delete original MP3
                os.remove(full_path)
                print(f"[SoundService] Deleted original MP3: {file_path}")

                current_path = wav_full_path
                new_file_path = wav_filename
            elif file_ext == '.wav':
                # WAV file - still normalize it
                temp_path = full_path + '.tmp.wav'
                print(f"[SoundService] Normalizing WAV: {file_path}")

                await asyncio.to_thread(
                    self.ffmpeg.convert_to_wav_normalized, full_path, temp_path
                )

                # Replace original with normalized
                os.remove(full_path)
                os.rename(temp_path, full_path)

            # 4. Extract duration (run in thread)
            duration = await asyncio.to_thread(self.ffmpeg.get_audio_duration, current_path)
            duration_int = int(duration)

            # 5. Generate waveform image (1200x300)
            waveform_bytes = await asyncio.to_thread(
                self.ffmpeg.generate_waveform_image, current_path, 1200, 300
            )

            # 6. Update database record
            sound.file_path = new_file_path
            sound.duration = duration_int
            sound.waveform = waveform_bytes
            sound.updated_at = datetime.utcnow()
            db.commit()

            print(f"[SoundService] Processed sound {sound_id}: "
                  f"duration={duration_int}s, waveform={len(waveform_bytes)} bytes, "
                  f"file_path={new_file_path}")

            # 7. Return success result
            return {
                "success": True,
                "id": sound_id,
                "duration": duration_int,
                "has_waveform": True,
                "file_path": new_file_path
            }

        except Exception as e:
            db.rollback()
            print(f"[SoundService] Error processing sound {sound_id}: {e}")
            return {
                "success": False,
                "id": sound_id,
                "error": str(e)
            }

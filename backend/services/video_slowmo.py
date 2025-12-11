"""
Video Slow Motion Service
Converts videos to slow motion with source-matched encoding parameters.
"""
import asyncio
import os
from typing import Callable, Any

from services.ffmpeg_service import FFmpegService


class VideoSlowmoService:
    """Service for converting videos to slow motion."""

    VIDEODATA_BASE = "/videodata"

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()

    async def convert_slowmo(
        self,
        input_path: str,
        speed_factor: float = 0.5,
        output_dir: str = None,
        progress_callback: Callable[[str, dict], Any] = None
    ) -> dict:
        """
        Convert video to slow motion.

        Args:
            input_path: Relative path to input video (e.g., "input/video.mp4")
            speed_factor: Speed multiplier (0.1 to 1.0, where 0.5 = 2x slower)
            output_dir: Relative output directory (default: same as input)
            progress_callback: Async callback for progress updates

        Returns:
            dict with:
            - success: bool
            - input: input path
            - output: output path
            - speed_factor: speed used
            - original_duration: source video duration
            - output_duration: resulting video duration
            - size_bytes: output file size
            - error: error message (if failed)
        """
        # Security check
        if '..' in input_path or (output_dir and '..' in output_dir):
            return {
                "success": False,
                "error": "Path traversal not allowed"
            }

        # Validate speed factor
        if speed_factor <= 0 or speed_factor > 1.0:
            return {
                "success": False,
                "error": "Speed factor must be between 0.1 and 1.0"
            }

        full_input = os.path.join(self.VIDEODATA_BASE, input_path)

        if not os.path.exists(full_input):
            return {
                "success": False,
                "error": f"Input file not found: {input_path}"
            }

        # Determine output directory
        if output_dir:
            full_output_dir = os.path.join(self.VIDEODATA_BASE, output_dir)
        else:
            full_output_dir = os.path.dirname(full_input)

        os.makedirs(full_output_dir, mode=0o755, exist_ok=True)

        try:
            # Get video info
            info = await asyncio.to_thread(self.ffmpeg.get_video_info, full_input)
            original_duration = info['duration']
            output_duration = original_duration / speed_factor

            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            ext = os.path.splitext(input_path)[1]
            output_name = f"{base_name}_slowmo_{speed_factor}x{ext}"
            output_path = os.path.join(full_output_dir, output_name)
            relative_output = os.path.relpath(output_path, self.VIDEODATA_BASE)

            # Notify start
            if progress_callback:
                await progress_callback("slowmo_started", {
                    "input": input_path,
                    "output": relative_output,
                    "speed_factor": speed_factor,
                    "original_duration": round(original_duration, 2),
                    "estimated_output_duration": round(output_duration, 2)
                })

            # Convert to slowmo (blocking in thread)
            await asyncio.to_thread(
                self.ffmpeg.convert_to_slowmo,
                full_input, output_path, speed_factor
            )

            # Get output file size
            file_size = os.path.getsize(output_path)

            result = {
                "success": True,
                "input": input_path,
                "output": relative_output,
                "speed_factor": speed_factor,
                "original_duration": round(original_duration, 2),
                "output_duration": round(output_duration, 2),
                "size_bytes": file_size
            }

            if progress_callback:
                await progress_callback("slowmo_completed", result)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "input": input_path,
                "error": str(e)
            }

            if progress_callback:
                await progress_callback("slowmo_error", error_result)

            return error_result

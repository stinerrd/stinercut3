"""
Video Splitter Service
Splits video files at keyframe boundaries without re-encoding.
"""
import asyncio
import os
from typing import Callable, Any

from services.ffmpeg_service import FFmpegService


class VideoSplitterService:
    """Service for splitting videos at keyframe boundaries."""

    VIDEODATA_BASE = "/videodata"
    KEYFRAME_WARN_THRESHOLD = 5.0  # seconds

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()

    async def split_video(
        self,
        input_path: str,
        timestamps: list,
        output_dir: str = None,
        progress_callback: Callable[[str, dict], Any] = None
    ) -> dict:
        """
        Split video at specified timestamps (snapped to nearest keyframes).

        Args:
            input_path: Relative path to input video (e.g., "input/video.mp4")
            timestamps: List of split points in seconds (N timestamps = N+1 output files)
            output_dir: Relative output directory (default: same as input)
            progress_callback: Async callback for progress updates

        Returns:
            dict with:
            - success: bool
            - input: input path
            - snapped_timestamps: actual keyframe times used
            - outputs: list of output file info
            - warnings: list of warning messages
            - error: error message (if failed)
        """
        # Security check
        if '..' in input_path or (output_dir and '..' in output_dir):
            return {
                "success": False,
                "error": "Path traversal not allowed"
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

        warnings = []

        try:
            # Notify start
            if progress_callback:
                await progress_callback("split_started", {
                    "input": input_path,
                    "timestamps": timestamps
                })

            # Get keyframes (blocking FFmpeg call in thread)
            keyframes = await asyncio.to_thread(self.ffmpeg.get_keyframes, full_input)

            if not keyframes:
                return {
                    "success": False,
                    "error": "No keyframes found in video. Video may need re-encoding."
                }

            # Get video duration
            duration = await asyncio.to_thread(self.ffmpeg.get_duration, full_input)

            # Process and validate timestamps
            valid_timestamps = []
            for ts in sorted(timestamps):
                if ts < 0:
                    warnings.append(f"Ignoring negative timestamp: {ts}")
                    continue
                if ts >= duration:
                    warnings.append(f"Timestamp {ts}s exceeds video duration ({duration:.2f}s), clamping")
                    ts = duration - 0.1  # Small offset from end
                if ts > 0 and ts < duration:
                    valid_timestamps.append(ts)

            # Snap timestamps to nearest keyframes
            snapped = []
            for ts in valid_timestamps:
                keyframe, distance = self.ffmpeg.find_nearest_keyframe(keyframes, ts)
                snapped.append(keyframe)
                if distance > self.KEYFRAME_WARN_THRESHOLD:
                    warnings.append(
                        f"Timestamp {ts:.2f}s adjusted to keyframe at {keyframe:.2f}s "
                        f"({distance:.2f}s difference)"
                    )

            # Remove duplicates and sort
            snapped = sorted(set(snapped))

            if progress_callback:
                await progress_callback("keyframes_resolved", {
                    "requested": timestamps,
                    "snapped": snapped,
                    "warnings": warnings
                })

            # Build split points: [0.0, snap1, snap2, ..., duration]
            split_points = [0.0] + snapped + [duration]

            # Generate output files
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            ext = os.path.splitext(input_path)[1]

            output_files = []
            total_segments = len(split_points) - 1

            for i in range(total_segments):
                start = split_points[i]
                end = split_points[i + 1]

                # Skip segments shorter than 0.1s
                if end - start < 0.1:
                    continue

                output_name = f"{base_name}_part{i+1:02d}{ext}"
                output_path = os.path.join(full_output_dir, output_name)
                relative_output = os.path.relpath(output_path, self.VIDEODATA_BASE)

                if progress_callback:
                    await progress_callback("splitting_segment", {
                        "segment": i + 1,
                        "total": total_segments,
                        "start": start,
                        "end": end,
                        "output": output_name
                    })

                # Split segment (blocking in thread)
                await asyncio.to_thread(
                    self.ffmpeg.split_video_segment,
                    full_input, output_path, start, end
                )

                # Get output file size
                file_size = os.path.getsize(output_path)

                output_files.append({
                    "path": relative_output,
                    "start": round(start, 3),
                    "end": round(end, 3),
                    "duration": round(end - start, 3),
                    "size_bytes": file_size
                })

            result = {
                "success": True,
                "input": input_path,
                "snapped_timestamps": snapped,
                "outputs": output_files,
                "warnings": warnings
            }

            if progress_callback:
                await progress_callback("split_completed", result)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "input": input_path,
                "error": str(e),
                "warnings": warnings
            }

            if progress_callback:
                await progress_callback("split_error", error_result)

            return error_result

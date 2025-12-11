"""
Video Transition Service
Creates fade-out-in transitions between two videos with minimal re-encoding.
"""
import asyncio
import os
from typing import Callable, Any

from services.ffmpeg_service import FFmpegService


class VideoTransitionService:
    """Service for creating video transitions with crossfade effects."""

    VIDEODATA_BASE = "/videodata"
    DEFAULT_TRANSITION_DURATION = 1.0  # seconds

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()

    def _compare_video_params(self, params1: dict, params2: dict) -> list:
        """
        Compare video parameters and return list of mismatches.

        Returns empty list if videos are compatible.
        """
        mismatches = []

        if params1['codec'] != params2['codec']:
            mismatches.append(f"codec: {params1['codec']} vs {params2['codec']}")

        if params1['width'] != params2['width'] or params1['height'] != params2['height']:
            mismatches.append(
                f"resolution: {params1['width']}x{params1['height']} vs "
                f"{params2['width']}x{params2['height']}"
            )

        # Allow small FPS differences (e.g., 29.97 vs 30)
        fps1 = params1['fps'] or 30
        fps2 = params2['fps'] or 30
        if abs(fps1 - fps2) > 1:
            mismatches.append(f"fps: {fps1} vs {fps2}")

        return mismatches

    async def create_transition(
        self,
        file1_path: str,
        file2_path: str,
        output_dir: str = None,
        transition_duration: float = None,
        keep_intermediate: bool = True,
        transition_only: bool = False,
        progress_callback: Callable[[str, dict], Any] = None
    ) -> dict:
        """
        Create fade-out-in transition between two videos.

        Process:
        1. Extract file1[0 to duration-N] (stream copy) -> part1
        2. Extract file1[duration-N to duration] -> transition_src1
        3. Extract file2[0 to N] -> transition_src2
        4. Extract file2[N to end] (stream copy) -> part2
        5. Create crossfade between transition sources (re-encode)
        6. Concatenate: part1 + transition + part2 (stream copy) [skip if transition_only]

        Args:
            file1_path: Relative path to first video
            file2_path: Relative path to second video
            output_dir: Output directory (default: same as file1)
            transition_duration: Crossfade duration in seconds (default: 1.0)
            keep_intermediate: Keep intermediate segment files (default: True)
            transition_only: Only create transition segment, skip joining (default: False)
            progress_callback: Async callback for progress updates

        Returns:
            dict with success, outputs, intermediate_files, etc.
        """
        if transition_duration is None:
            transition_duration = self.DEFAULT_TRANSITION_DURATION

        # Security check
        if '..' in file1_path or '..' in file2_path:
            return {"success": False, "error": "Path traversal not allowed"}
        if output_dir and '..' in output_dir:
            return {"success": False, "error": "Path traversal not allowed"}

        full_file1 = os.path.join(self.VIDEODATA_BASE, file1_path)
        full_file2 = os.path.join(self.VIDEODATA_BASE, file2_path)

        # Check files exist
        if not os.path.exists(full_file1):
            return {"success": False, "error": f"File not found: {file1_path}"}
        if not os.path.exists(full_file2):
            return {"success": False, "error": f"File not found: {file2_path}"}

        # Determine output directory
        if output_dir:
            full_output_dir = os.path.join(self.VIDEODATA_BASE, output_dir)
        else:
            full_output_dir = os.path.dirname(full_file1)

        os.makedirs(full_output_dir, mode=0o755, exist_ok=True)

        intermediate_files = []

        try:
            # Notify start
            if progress_callback:
                await progress_callback("transition_started", {
                    "file1": file1_path,
                    "file2": file2_path,
                    "transition_duration": transition_duration,
                    "transition_only": transition_only
                })

            # Get video info for both files
            params1 = await asyncio.to_thread(self.ffmpeg.get_video_encoding_params, full_file1)
            params2 = await asyncio.to_thread(self.ffmpeg.get_video_encoding_params, full_file2)

            # Check compatibility
            mismatches = self._compare_video_params(params1, params2)
            if mismatches:
                return {
                    "success": False,
                    "error": f"Video parameters mismatch: {', '.join(mismatches)}"
                }

            # Get durations
            duration1 = await asyncio.to_thread(self.ffmpeg.get_duration, full_file1)
            duration2 = await asyncio.to_thread(self.ffmpeg.get_duration, full_file2)

            # Validate durations
            if duration1 <= transition_duration:
                return {
                    "success": False,
                    "error": f"File1 duration ({duration1:.2f}s) must be greater than transition duration ({transition_duration}s)"
                }
            if duration2 <= transition_duration:
                return {
                    "success": False,
                    "error": f"File2 duration ({duration2:.2f}s) must be greater than transition duration ({transition_duration}s)"
                }

            # Get audio info
            audio_params = await asyncio.to_thread(self.ffmpeg.get_audio_info, full_file1)

            # Generate output filenames
            base1 = os.path.splitext(os.path.basename(file1_path))[0]
            base2 = os.path.splitext(os.path.basename(file2_path))[0]
            ext = os.path.splitext(file1_path)[1]

            trans_src1_path = os.path.join(full_output_dir, f"{base1}_trans_src{ext}")
            trans_src2_path = os.path.join(full_output_dir, f"{base2}_trans_src{ext}")
            transition_path = os.path.join(full_output_dir, f"{base1}_{base2}_transition{ext}")

            # These are only needed if not transition_only
            part1_path = None
            part2_path = None
            final_path = None

            if not transition_only:
                part1_path = os.path.join(full_output_dir, f"{base1}_part1{ext}")
                part2_path = os.path.join(full_output_dir, f"{base2}_part2{ext}")
                final_path = os.path.join(full_output_dir, f"{base1}_{base2}_joined{ext}")

                # Step 1: Extract part1 (file1 from 0 to duration1 - transition_duration)
                if progress_callback:
                    await progress_callback("extracting_part1", {
                        "file": file1_path,
                        "start": 0,
                        "end": duration1 - transition_duration
                    })

                await asyncio.to_thread(
                    self.ffmpeg.split_video_segment,
                    full_file1, part1_path,
                    start_time=None,
                    end_time=duration1 - transition_duration
                )
                intermediate_files.append(os.path.relpath(part1_path, self.VIDEODATA_BASE))

            # Step 2: Extract transition source from file1 (last N seconds)
            if progress_callback:
                await progress_callback("extracting_transition_clips", {
                    "clip1_range": [duration1 - transition_duration, duration1],
                    "clip2_range": [0, transition_duration]
                })

            await asyncio.to_thread(
                self.ffmpeg.split_video_segment,
                full_file1, trans_src1_path,
                start_time=duration1 - transition_duration,
                end_time=None
            )
            intermediate_files.append(os.path.relpath(trans_src1_path, self.VIDEODATA_BASE))

            # Step 3: Extract transition source from file2 (first N seconds)
            await asyncio.to_thread(
                self.ffmpeg.split_video_segment,
                full_file2, trans_src2_path,
                start_time=None,
                end_time=transition_duration
            )
            intermediate_files.append(os.path.relpath(trans_src2_path, self.VIDEODATA_BASE))

            if not transition_only:
                # Step 4: Extract part2 (file2 from transition_duration to end)
                if progress_callback:
                    await progress_callback("extracting_part2", {
                        "file": file2_path,
                        "start": transition_duration,
                        "end": duration2
                    })

                await asyncio.to_thread(
                    self.ffmpeg.split_video_segment,
                    full_file2, part2_path,
                    start_time=transition_duration,
                    end_time=None
                )
                intermediate_files.append(os.path.relpath(part2_path, self.VIDEODATA_BASE))

            # Step 5: Create crossfade transition (this part requires re-encoding)
            if progress_callback:
                await progress_callback("creating_crossfade", {
                    "fade_duration": transition_duration,
                    "transition_type": "fade"
                })

            await asyncio.to_thread(
                self.ffmpeg.create_xfade_transition,
                trans_src1_path, trans_src2_path, transition_path,
                fade_duration=transition_duration,
                video_params=params1,
                audio_params=audio_params,
                transition_type="fade"
            )

            # Get transition output info
            transition_duration_actual = await asyncio.to_thread(self.ffmpeg.get_duration, transition_path)
            transition_size = os.path.getsize(transition_path)

            if transition_only:
                # Clean up transition source files if not keeping intermediate
                if not keep_intermediate:
                    for f in [trans_src1_path, trans_src2_path]:
                        if os.path.exists(f):
                            os.unlink(f)
                    intermediate_files = []

                result = {
                    "success": True,
                    "output": os.path.relpath(transition_path, self.VIDEODATA_BASE),
                    "output_duration": round(transition_duration_actual, 3),
                    "size_bytes": transition_size,
                    "intermediate_files": intermediate_files if keep_intermediate else [],
                    "file1": file1_path,
                    "file2": file2_path,
                    "transition_duration": transition_duration,
                    "transition_only": True
                }

                if progress_callback:
                    await progress_callback("transition_completed", result)

                return result

            # Add transition to intermediate files for full join mode
            intermediate_files.append(os.path.relpath(transition_path, self.VIDEODATA_BASE))

            # Step 6: Concatenate all parts (stream copy - lossless)
            if progress_callback:
                await progress_callback("concatenating", {
                    "segments": 3
                })

            await asyncio.to_thread(
                self.ffmpeg.concatenate_videos,
                [part1_path, transition_path, part2_path],
                final_path
            )

            # Get final output info
            final_duration = await asyncio.to_thread(self.ffmpeg.get_duration, final_path)
            final_size = os.path.getsize(final_path)

            # Clean up transition source files if not keeping intermediate
            if not keep_intermediate:
                for f in [trans_src1_path, trans_src2_path]:
                    if os.path.exists(f):
                        os.unlink(f)
                intermediate_files = [
                    f for f in intermediate_files
                    if not f.endswith('_trans_src' + ext)
                ]

            result = {
                "success": True,
                "output": os.path.relpath(final_path, self.VIDEODATA_BASE),
                "output_duration": round(final_duration, 3),
                "size_bytes": final_size,
                "intermediate_files": intermediate_files if keep_intermediate else [],
                "file1": file1_path,
                "file2": file2_path,
                "transition_duration": transition_duration,
                "transition_only": False
            }

            if progress_callback:
                await progress_callback("transition_completed", result)

            return result

        except Exception as e:
            # Clean up partial outputs on error
            cleanup_paths = [trans_src1_path, trans_src2_path, transition_path]
            if part1_path:
                cleanup_paths.append(part1_path)
            if part2_path:
                cleanup_paths.append(part2_path)
            if final_path:
                cleanup_paths.append(final_path)

            for path in cleanup_paths:
                try:
                    if path and os.path.exists(path):
                        os.unlink(path)
                except:
                    pass

            error_result = {
                "success": False,
                "file1": file1_path,
                "file2": file2_path,
                "error": str(e)
            }

            if progress_callback:
                await progress_callback("transition_error", error_result)

            return error_result

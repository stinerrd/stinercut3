"""
FFmpeg Service
Encapsulates FFmpeg/ffprobe operations for video and audio processing.
"""
import bisect
import os

import ffmpeg


class FFmpegService:
    """Encapsulates FFmpeg/ffprobe operations."""

    # =====================
    # Video operations
    # =====================

    def get_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe."""
        try:
            probe = ffmpeg.probe(video_path)
            return float(probe['format']['duration'])
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to probe video: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def extract_frame(self, video_path: str, timestamp: float) -> bytes:
        """Extract a single frame at timestamp as PNG bytes."""
        try:
            out, _ = (
                ffmpeg
                .input(video_path, ss=timestamp)
                .output('pipe:', vframes=1, format='image2', vcodec='png')
                .run(capture_stdout=True, capture_stderr=True)
            )
            return out
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to extract frame: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def extract_thumbnail_jpeg(self, video_path: str, timestamp: float) -> bytes:
        """Extract a single frame at timestamp as JPEG bytes."""
        try:
            out, _ = (
                ffmpeg
                .input(video_path, ss=timestamp)
                .output('pipe:', vframes=1, format='image2', vcodec='mjpeg', **{'q:v': 2})
                .run(capture_stdout=True, capture_stderr=True)
            )
            return out
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to extract thumbnail: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def get_video_info(self, video_path: str) -> dict:
        """
        Get video metadata.

        Returns dict with: duration, width, height, codec, fps
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )

            fps = None
            if video_stream and 'r_frame_rate' in video_stream:
                rate = video_stream['r_frame_rate']
                if '/' in rate:
                    num, den = rate.split('/')
                    fps = int(num) / int(den) if int(den) != 0 else None
                else:
                    fps = float(rate)

            return {
                'duration': float(probe['format']['duration']),
                'width': video_stream['width'] if video_stream else None,
                'height': video_stream['height'] if video_stream else None,
                'codec': video_stream.get('codec_name') if video_stream else None,
                'fps': fps,
            }
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to get video info: {e.stderr.decode() if e.stderr else str(e)}"
            )

    # =====================
    # Keyframe operations
    # =====================

    def get_keyframes(self, video_path: str) -> list:
        """
        Get all keyframe timestamps from video using ffprobe.

        Uses packet-level analysis (fast) instead of frame decoding (slow).
        Keyframes are identified by the 'K' flag in packet flags.

        Args:
            video_path: Path to video file

        Returns:
            List of keyframe timestamps in seconds, sorted ascending
        """
        try:
            probe = ffmpeg.probe(
                video_path,
                select_streams='v:0',
                show_entries='packet=pts_time,flags'
            )

            keyframes = []
            for packet in probe.get('packets', []):
                flags = packet.get('flags', '')
                if 'K' in flags:
                    pts_time = packet.get('pts_time')
                    if pts_time:
                        keyframes.append(float(pts_time))

            return sorted(keyframes)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to get keyframes: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def find_nearest_keyframe(self, keyframes: list, target: float) -> tuple:
        """
        Find the keyframe nearest to target timestamp.

        Args:
            keyframes: Sorted list of keyframe timestamps
            target: Desired timestamp in seconds

        Returns:
            Tuple of (keyframe_time, distance_from_target)
        """
        if not keyframes:
            return target, 0.0

        pos = bisect.bisect_left(keyframes, target)

        candidates = []
        if pos > 0:
            candidates.append(keyframes[pos - 1])
        if pos < len(keyframes):
            candidates.append(keyframes[pos])

        if not candidates:
            return keyframes[-1], abs(target - keyframes[-1])

        nearest = min(candidates, key=lambda k: abs(k - target))
        return nearest, abs(nearest - target)

    def split_video_segment(
        self,
        input_path: str,
        output_path: str,
        start_time: float = None,
        end_time: float = None
    ) -> None:
        """
        Extract a segment from video using stream copy (lossless, no re-encoding).

        Args:
            input_path: Source video path
            output_path: Destination video path
            start_time: Start timestamp in seconds (None for beginning)
            end_time: End timestamp in seconds (None for end)
        """
        try:
            # Build input with optional seek
            input_kwargs = {}
            if start_time is not None and start_time > 0:
                input_kwargs['ss'] = start_time

            stream = ffmpeg.input(input_path, **input_kwargs)

            # Build output with optional duration
            output_kwargs = {
                'c': 'copy',
                'avoid_negative_ts': '1'
            }
            if end_time is not None:
                duration = end_time - (start_time or 0)
                output_kwargs['t'] = duration

            stream = ffmpeg.output(stream, output_path, **output_kwargs)
            stream = ffmpeg.overwrite_output(stream)

            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            os.chmod(output_path, 0o644)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to split video: {e.stderr.decode() if e.stderr else str(e)}"
            )

    # =====================
    # Audio operations
    # =====================

    def get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration in seconds using ffprobe."""
        try:
            probe = ffmpeg.probe(audio_path)
            return float(probe['format']['duration'])
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to probe audio: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def convert_to_wav_normalized(self, input_path: str, output_path: str) -> None:
        """
        Convert audio to WAV format with loudness normalization.
        Uses EBU R128 loudness standard (I=-23, TP=-1.5, LRA=11).

        Args:
            input_path: Path to source audio file (MP3 or WAV)
            output_path: Path for output WAV file
        """
        try:
            (
                ffmpeg
                .input(input_path)
                .filter('loudnorm', I=-23, TP=-1.5, LRA=11)
                .output(output_path, acodec='pcm_s16le', ar=44100)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            # Set file permissions
            os.chmod(output_path, 0o644)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to convert audio: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def generate_waveform_image(self, audio_path: str, width: int = 1200, height: int = 300) -> bytes:
        """
        Generate a waveform image (PNG) from an audio file.

        Args:
            audio_path: Path to audio file
            width: Image width in pixels (default 1200)
            height: Image height in pixels (default 300)

        Returns:
            PNG image as bytes
        """
        try:
            out, _ = (
                ffmpeg
                .input(audio_path)
                .filter('showwavespic', s=f'{width}x{height}', colors='#3498db', scale='sqrt', draw='full')
                .output('pipe:', vframes=1, format='image2', vcodec='png')
                .run(capture_stdout=True, capture_stderr=True)
            )
            return out
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to generate waveform: {e.stderr.decode() if e.stderr else str(e)}"
            )

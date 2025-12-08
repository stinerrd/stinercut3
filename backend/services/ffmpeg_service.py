"""
FFmpeg Service
Encapsulates FFmpeg/ffprobe operations for video processing.
"""
import ffmpeg


class FFmpegService:
    """Encapsulates FFmpeg/ffprobe operations."""

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

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
    # Slow motion operations
    # =====================

    def get_video_encoding_params(self, video_path: str) -> dict:
        """
        Get detailed video encoding parameters for matching during re-encode.

        Returns dict with: codec, width, height, fps, bitrate, profile, level, pix_fmt
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'),
                None
            )

            if not video_stream:
                raise ValueError("No video stream found")

            # Parse framerate
            fps = 30  # default
            if 'r_frame_rate' in video_stream:
                rate = video_stream['r_frame_rate']
                if '/' in rate:
                    num, den = rate.split('/')
                    fps = int(num) / int(den) if int(den) != 0 else 30
                else:
                    fps = float(rate)

            # Get bitrate (from stream or format)
            bitrate = video_stream.get('bit_rate')
            if not bitrate:
                bitrate = probe['format'].get('bit_rate')
            bitrate = int(bitrate) if bitrate else 45_000_000  # 45Mbps default

            return {
                'codec': video_stream.get('codec_name', 'h264'),
                'width': video_stream.get('width'),
                'height': video_stream.get('height'),
                'fps': fps,
                'bitrate': bitrate,
                'profile': video_stream.get('profile', 'High'),
                'level': video_stream.get('level', 42),
                'pix_fmt': video_stream.get('pix_fmt', 'yuv420p'),
            }
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to get encoding params: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def convert_to_slowmo(
        self,
        input_path: str,
        output_path: str,
        speed_factor: float = 0.5
    ) -> None:
        """
        Convert video to slow motion, matching source encoding parameters.

        Args:
            input_path: Source video path
            output_path: Destination video path
            speed_factor: Speed multiplier (0.5 = 2x slower, 0.25 = 4x slower)
        """
        try:
            # Get source encoding parameters
            params = self.get_video_encoding_params(input_path)

            # Map codec to encoder
            encoder_map = {
                'h264': 'libx264',
                'hevc': 'libx265',
                'h265': 'libx265',
            }
            encoder = encoder_map.get(params['codec'], 'libx264')

            # Convert level (42 -> "4.2")
            level = params['level']
            if isinstance(level, int) and level > 10:
                level = f"{level // 10}.{level % 10}"

            # Calculate PTS multiplier (inverse of speed)
            pts_multiplier = 1.0 / speed_factor

            # Build output kwargs to match source
            output_kwargs = {
                'vcodec': encoder,
                'video_bitrate': params['bitrate'],
                'maxrate': params['bitrate'],
                'bufsize': params['bitrate'] * 2,
                'r': params['fps'],
                'pix_fmt': params['pix_fmt'],
                'an': None,  # no audio
            }

            # Add profile/level for h264
            if encoder == 'libx264':
                profile = params['profile'].lower() if params['profile'] else 'high'
                # Normalize profile name
                if profile not in ('baseline', 'main', 'high', 'high10', 'high422', 'high444'):
                    profile = 'high'
                output_kwargs['profile:v'] = profile
                output_kwargs['level'] = level

            stream = (
                ffmpeg
                .input(input_path)
                .filter('setpts', f'{pts_multiplier}*PTS')
                .output(output_path, **output_kwargs)
                .overwrite_output()
            )

            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            os.chmod(output_path, 0o644)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to convert to slowmo: {e.stderr.decode() if e.stderr else str(e)}"
            )

    # =====================
    # Transition operations
    # =====================

    def get_audio_info(self, video_path: str) -> dict:
        """
        Get audio stream information from a video file.

        Returns dict with: codec, sample_rate, channels, bitrate
        Returns None values if no audio stream exists.
        """
        try:
            probe = ffmpeg.probe(video_path)
            audio_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'audio'),
                None
            )

            if not audio_stream:
                return {
                    'codec': None,
                    'sample_rate': None,
                    'channels': None,
                    'bitrate': None,
                }

            return {
                'codec': audio_stream.get('codec_name'),
                'sample_rate': int(audio_stream.get('sample_rate', 48000)),
                'channels': audio_stream.get('channels', 2),
                'bitrate': int(audio_stream.get('bit_rate', 128000)) if audio_stream.get('bit_rate') else 128000,
            }
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to get audio info: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def create_xfade_transition(
        self,
        clip1_path: str,
        clip2_path: str,
        output_path: str,
        fade_duration: float,
        video_params: dict,
        audio_params: dict = None,
        transition_type: str = "fade"
    ) -> None:
        """
        Create crossfade transition between two video clips.

        The output is encoded to match the source video parameters for seamless
        concatenation with stream copy.

        Args:
            clip1_path: First clip (fade out)
            clip2_path: Second clip (fade in)
            output_path: Output video path
            fade_duration: Duration of crossfade in seconds
            video_params: Video encoding parameters (from get_video_encoding_params)
            audio_params: Audio parameters (from get_audio_info), optional
            transition_type: xfade transition type (fade, wipeleft, etc.)
        """
        try:
            # Get clip1 duration for xfade offset calculation
            clip1_duration = self.get_duration(clip1_path)

            # xfade offset = when transition starts (relative to clip1)
            # For equal-length clips where we want full crossfade:
            # offset = clip1_duration - fade_duration
            offset = clip1_duration - fade_duration

            # Input streams
            in1 = ffmpeg.input(clip1_path)
            in2 = ffmpeg.input(clip2_path)

            # Apply xfade filter to video streams
            video = ffmpeg.filter(
                [in1.video, in2.video],
                'xfade',
                transition=transition_type,
                duration=fade_duration,
                offset=offset
            )

            # Map codec to encoder
            encoder_map = {
                'h264': 'libx264',
                'hevc': 'libx265',
                'h265': 'libx265',
            }
            encoder = encoder_map.get(video_params['codec'], 'libx264')

            # Convert level (42 -> "4.2")
            level = video_params.get('level', 42)
            if isinstance(level, int) and level > 10:
                level = f"{level // 10}.{level % 10}"

            # Build video output kwargs
            output_kwargs = {
                'vcodec': encoder,
                'video_bitrate': video_params['bitrate'],
                'maxrate': video_params['bitrate'],
                'bufsize': video_params['bitrate'] * 2,
                'r': video_params['fps'],
                'pix_fmt': video_params.get('pix_fmt', 'yuv420p'),
            }

            # Add profile/level for h264
            if encoder == 'libx264':
                profile = video_params.get('profile', 'High')
                if profile:
                    profile = profile.lower()
                    if profile not in ('baseline', 'main', 'high', 'high10', 'high422', 'high444'):
                        profile = 'high'
                    output_kwargs['profile:v'] = profile
                output_kwargs['level'] = level

            # Handle audio if present
            if audio_params and audio_params.get('codec'):
                # Apply acrossfade filter to audio streams
                audio = ffmpeg.filter(
                    [in1.audio, in2.audio],
                    'acrossfade',
                    d=fade_duration,
                    c1='tri',
                    c2='tri'
                )
                output_kwargs['acodec'] = 'aac'
                output_kwargs['audio_bitrate'] = audio_params.get('bitrate', 128000)
                output_kwargs['ar'] = audio_params.get('sample_rate', 48000)

                stream = ffmpeg.output(video, audio, output_path, **output_kwargs)
            else:
                # No audio
                output_kwargs['an'] = None
                stream = ffmpeg.output(video, output_path, **output_kwargs)

            stream = ffmpeg.overwrite_output(stream)
            ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
            os.chmod(output_path, 0o644)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to create xfade transition: {e.stderr.decode() if e.stderr else str(e)}"
            )

    def concatenate_videos(
        self,
        video_paths: list,
        output_path: str
    ) -> None:
        """
        Concatenate multiple videos using concat demuxer with stream copy (lossless).

        All videos must have compatible codecs for stream copy to work.

        Args:
            video_paths: List of video file paths (in order)
            output_path: Output video path
        """
        import tempfile

        try:
            # Create concat file list
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for path in video_paths:
                    # Escape single quotes in path
                    escaped_path = path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
                concat_file = f.name

            try:
                stream = ffmpeg.input(concat_file, format='concat', safe=0)
                stream = ffmpeg.output(stream, output_path, c='copy')
                stream = ffmpeg.overwrite_output(stream)
                ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)
                os.chmod(output_path, 0o644)
            finally:
                os.unlink(concat_file)
        except ffmpeg.Error as e:
            raise ValueError(
                f"Failed to concatenate videos: {e.stderr.decode() if e.stderr else str(e)}"
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

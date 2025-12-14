"""
Video Vertical Service
Converts horizontal 16:9 videos to vertical 9:16 format for Shorts/Reels.
Supports center crop and smart face tracking.
"""
import asyncio
import os
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Any, List, Optional

import cv2
import numpy as np

from services.ffmpeg_service import FFmpegService


class CropMethod(str, Enum):
    """Crop method for vertical video creation."""
    CENTER = "center"
    FACE_TRACKING = "face_tracking"


@dataclass
class CropParams:
    """Crop parameters calculated from source dimensions."""
    crop_w: int      # Width of crop window (9:16 aspect)
    crop_h: int      # Height of crop window (full source height)
    max_x: int       # Maximum valid crop X offset
    center_x: int    # Center crop X offset


@dataclass
class FaceDetection:
    """Detected face bounding box."""
    x: int
    y: int
    width: int
    height: int
    confidence: float


class CropSmoother:
    """
    Exponential Moving Average smoother for crop positions.
    Prevents jerky camera movement in face tracking mode.
    """

    def __init__(
        self,
        smoothing_factor: float = 0.15,
        velocity_damping: float = 0.8,
        max_velocity: float = 50.0
    ):
        """
        Args:
            smoothing_factor: Lower = smoother (0.1-0.3 recommended)
            velocity_damping: Reduces oscillation
            max_velocity: Max pixels per frame to prevent jumps
        """
        self.smoothing = smoothing_factor
        self.damping = velocity_damping
        self.max_velocity = max_velocity

    def smooth(self, raw_positions: List[int], max_x: int) -> List[int]:
        """
        Apply EMA smoothing to crop positions.

        Args:
            raw_positions: List of raw crop X positions
            max_x: Maximum valid crop X

        Returns:
            Smoothed positions
        """
        if not raw_positions:
            return []

        if len(raw_positions) == 1:
            return raw_positions

        smoothed = []
        current_x = float(raw_positions[0])
        velocity_x = 0.0

        for target_x in raw_positions:
            # Calculate desired velocity toward target
            desired_velocity = (target_x - current_x) * self.smoothing

            # Apply damping to reduce oscillation
            velocity_x = velocity_x * self.damping + desired_velocity * (1 - self.damping)

            # Clamp maximum velocity
            velocity_x = max(-self.max_velocity, min(self.max_velocity, velocity_x))

            # Update position
            current_x += velocity_x

            # Clamp to valid range
            current_x = max(0, min(max_x, current_x))

            smoothed.append(int(round(current_x)))

        return smoothed


class FaceDetector:
    """
    Face detector using OpenCV's YuNet DNN.
    Optimized for detecting faces in tandem skydiving videos (2 people).
    """

    _detector = None  # Singleton

    MODEL_PATH = "/videodata/models/face_detection_yunet_2023mar.onnx"
    FALLBACK_HAAR = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

    def __init__(
        self,
        score_threshold: float = 0.6,
        nms_threshold: float = 0.3,
        top_k: int = 5
    ):
        self.score_threshold = score_threshold
        self.nms_threshold = nms_threshold
        self.top_k = top_k
        self._haar_cascade = None

    def _get_detector(self, input_size: tuple):
        """Get or create YuNet detector."""
        if os.path.exists(self.MODEL_PATH):
            try:
                detector = cv2.FaceDetectorYN.create(
                    self.MODEL_PATH,
                    "",
                    input_size,
                    self.score_threshold,
                    self.nms_threshold,
                    self.top_k
                )
                return detector
            except Exception:
                pass
        return None

    def _get_haar_cascade(self):
        """Fallback to Haar cascade if YuNet not available."""
        if self._haar_cascade is None:
            self._haar_cascade = cv2.CascadeClassifier(self.FALLBACK_HAAR)
        return self._haar_cascade

    def detect(self, frame: np.ndarray) -> List[FaceDetection]:
        """
        Detect faces in frame.

        Args:
            frame: BGR image (numpy array)

        Returns:
            List of FaceDetection objects
        """
        h, w = frame.shape[:2]

        # Try YuNet first
        detector = self._get_detector((w, h))
        if detector is not None:
            return self._detect_yunet(detector, frame)

        # Fallback to Haar cascade
        return self._detect_haar(frame)

    def _detect_yunet(self, detector, frame: np.ndarray) -> List[FaceDetection]:
        """Detect faces using YuNet DNN."""
        h, w = frame.shape[:2]
        detector.setInputSize((w, h))

        _, faces = detector.detect(frame)

        detections = []
        if faces is not None:
            for face in faces:
                x, y, fw, fh = int(face[0]), int(face[1]), int(face[2]), int(face[3])
                confidence = float(face[14]) if len(face) > 14 else 1.0
                detections.append(FaceDetection(x, y, fw, fh, confidence))

        return detections

    def _detect_haar(self, frame: np.ndarray) -> List[FaceDetection]:
        """Detect faces using Haar cascade (fallback)."""
        cascade = self._get_haar_cascade()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE
        )

        return [
            FaceDetection(x, y, w, h, 1.0)
            for (x, y, w, h) in faces
        ]


class VideoVerticalService:
    """Service for converting horizontal videos to vertical format."""

    VIDEODATA_BASE = "/videodata"

    # Analysis settings
    FACE_SAMPLE_FPS = 2  # Sample at 2 FPS for face detection (faster)
    MAX_HOLD_FRAMES = 60  # Hold last position for up to 2 seconds (at 30fps)
    MAX_INTERPOLATION_GAP = 90  # Max frames to interpolate (3 sec at 30fps)
    DETECTION_SCALE = 0.5  # Scale down frames for faster detection
    BATCH_SIZE = 8  # Process frames in batches

    def __init__(self, ffmpeg_service: FFmpegService = None):
        self.ffmpeg = ffmpeg_service or FFmpegService()
        self.face_detector = FaceDetector()
        self.crop_smoother = CropSmoother()

    def calculate_crop_params(self, width: int, height: int) -> CropParams:
        """
        Calculate crop parameters for any 16:9 source.

        Args:
            width: Source video width
            height: Source video height

        Returns:
            CropParams with crop dimensions and offsets
        """
        crop_w = int(height * 9 / 16)
        max_x = width - crop_w
        center_x = max_x // 2
        return CropParams(
            crop_w=crop_w,
            crop_h=height,
            max_x=max_x,
            center_x=center_x
        )

    def calculate_crop_x_from_faces(
        self,
        faces: List[FaceDetection],
        crop_params: CropParams
    ) -> int:
        """
        Calculate crop X position to center detected faces.

        Args:
            faces: List of detected faces
            crop_params: Crop parameters

        Returns:
            crop_x position (0 to max_x)
        """
        if not faces:
            return crop_params.center_x

        # Calculate bounding box encompassing all faces
        all_x = []
        for face in faces:
            all_x.extend([face.x, face.x + face.width])

        faces_min_x = min(all_x)
        faces_max_x = max(all_x)
        faces_center_x = (faces_min_x + faces_max_x) / 2

        # Calculate crop_x to center faces
        ideal_crop_x = faces_center_x - (crop_params.crop_w / 2)

        # Clamp to valid range
        return max(0, min(crop_params.max_x, int(ideal_crop_x)))

    async def analyze_video_faces(
        self,
        video_path: str,
        crop_params: CropParams,
        fps: float,
        duration: float,
        progress_callback: Callable[[str, dict], Any] = None
    ) -> List[int]:
        """
        Analyze video and generate crop positions based on face detection.

        Optimized version using:
        - FFmpeg for fast frame extraction at specific timestamps
        - Scaled down frames for faster detection
        - Concurrent processing

        Args:
            video_path: Full path to video
            crop_params: Crop parameters
            fps: Video FPS
            duration: Video duration in seconds
            progress_callback: Progress callback

        Returns:
            List of crop_x positions (one per frame at video FPS)
        """
        import concurrent.futures

        total_frames = int(duration * fps)
        sample_interval = 1.0 / self.FACE_SAMPLE_FPS  # seconds between samples

        # Generate sample timestamps
        timestamps = []
        t = 0.0
        while t < duration:
            timestamps.append(t)
            t += sample_interval

        total_samples = len(timestamps)

        if progress_callback:
            await progress_callback("vertical_analyzing", {
                "progress": 0,
                "samples_processed": 0,
                "total_samples": total_samples,
                "faces_in_frame": 0
            })

        # Process frames in parallel batches
        sample_positions = {}
        samples_processed = 0
        last_faces_count = 0

        # Use ThreadPoolExecutor for parallel frame extraction and detection
        def extract_and_detect(timestamp: float) -> tuple:
            """Extract frame at timestamp and detect faces."""
            try:
                # Use FFmpeg to extract single frame (much faster than OpenCV seek)
                import subprocess

                # Calculate scaled dimensions
                scale_w = int(crop_params.crop_w + crop_params.max_x) * self.DETECTION_SCALE
                scale_h = int(crop_params.crop_h * self.DETECTION_SCALE)

                cmd = [
                    'ffmpeg', '-ss', str(timestamp), '-i', video_path,
                    '-vframes', '1', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                    '-vf', f'scale={int(scale_w)}:{int(scale_h)}',
                    '-loglevel', 'error', 'pipe:1'
                ]

                result = subprocess.run(cmd, capture_output=True, timeout=10)

                if result.returncode != 0 or not result.stdout:
                    return (timestamp, None, [])

                # Convert raw bytes to numpy array
                frame = np.frombuffer(result.stdout, dtype=np.uint8)
                frame = frame.reshape((int(scale_h), int(scale_w), 3))

                # Detect faces on scaled frame
                faces = self.face_detector.detect(frame)

                # Scale face coordinates back to original resolution
                scale_factor = 1.0 / self.DETECTION_SCALE
                scaled_faces = [
                    FaceDetection(
                        x=int(f.x * scale_factor),
                        y=int(f.y * scale_factor),
                        width=int(f.width * scale_factor),
                        height=int(f.height * scale_factor),
                        confidence=f.confidence
                    )
                    for f in faces
                ]

                return (timestamp, frame, scaled_faces)
            except Exception as e:
                return (timestamp, None, [])

        # Process in batches with ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all tasks
            future_to_ts = {
                executor.submit(extract_and_detect, ts): ts
                for ts in timestamps
            }

            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_ts):
                timestamp, frame, faces = future.result()

                # Calculate frame index from timestamp
                frame_idx = int(timestamp * fps)

                # Calculate crop position
                crop_x = self.calculate_crop_x_from_faces(faces, crop_params)
                sample_positions[frame_idx] = crop_x

                samples_processed += 1
                last_faces_count = len(faces)

                # Report progress
                if progress_callback and samples_processed % 5 == 0:
                    progress = (samples_processed / total_samples) * 100
                    await progress_callback("vertical_analyzing", {
                        "progress": round(progress, 1),
                        "samples_processed": samples_processed,
                        "faces_in_frame": last_faces_count
                    })

        # Final progress update
        if progress_callback:
            await progress_callback("vertical_analyzing", {
                "progress": 100,
                "samples_processed": samples_processed,
                "faces_in_frame": last_faces_count
            })

        # Interpolate positions for all frames
        all_positions = self._interpolate_positions(
            sample_positions, total_frames, crop_params.center_x
        )

        # Apply smoothing
        smoothed = self.crop_smoother.smooth(all_positions, crop_params.max_x)

        return smoothed

    def _interpolate_positions(
        self,
        sample_positions: dict,
        total_frames: int,
        fallback_x: int
    ) -> List[int]:
        """
        Interpolate crop positions for frames between samples.

        Args:
            sample_positions: Dict of frame_idx -> crop_x for sampled frames
            total_frames: Total number of frames
            fallback_x: Fallback position when no samples nearby

        Returns:
            List of crop_x for all frames
        """
        if not sample_positions:
            return [fallback_x] * total_frames

        positions = []
        sorted_samples = sorted(sample_positions.items())

        for frame_idx in range(total_frames):
            if frame_idx in sample_positions:
                positions.append(sample_positions[frame_idx])
            else:
                # Find surrounding samples
                prev_sample = None
                next_sample = None

                for s_idx, s_x in sorted_samples:
                    if s_idx <= frame_idx:
                        prev_sample = (s_idx, s_x)
                    if s_idx > frame_idx and next_sample is None:
                        next_sample = (s_idx, s_x)
                        break

                if prev_sample and next_sample:
                    # Linear interpolation
                    gap = next_sample[0] - prev_sample[0]
                    if gap <= self.MAX_INTERPOLATION_GAP:
                        t = (frame_idx - prev_sample[0]) / gap
                        crop_x = int(prev_sample[1] + t * (next_sample[1] - prev_sample[1]))
                        positions.append(crop_x)
                    else:
                        # Gap too large, use nearest
                        positions.append(prev_sample[1] if frame_idx - prev_sample[0] < next_sample[0] - frame_idx else next_sample[1])
                elif prev_sample:
                    # Hold last position
                    if frame_idx - prev_sample[0] < self.MAX_HOLD_FRAMES:
                        positions.append(prev_sample[1])
                    else:
                        positions.append(fallback_x)
                elif next_sample:
                    positions.append(next_sample[1])
                else:
                    positions.append(fallback_x)

        return positions

    async def convert_to_vertical(
        self,
        input_path: str,
        method: CropMethod = CropMethod.CENTER,
        output_size: str = "1080p",
        output_dir: str = None,
        center_offset: float = 0.0,
        progress_callback: Callable[[str, dict], Any] = None
    ) -> dict:
        """
        Convert video to vertical 9:16 format.

        Args:
            input_path: Relative path to input video
            method: CropMethod.CENTER or CropMethod.FACE_TRACKING
            output_size: "1080p", "720p", or "native"
            output_dir: Relative output directory (default: same as input)
            center_offset: Offset from center as percentage (-50 to +50).
                          Negative = left, Positive = right.
                          Example: -10 means 10% left of center
            progress_callback: Async callback for progress updates

        Returns:
            dict with success, output path, etc.
        """
        # Security check
        if '..' in input_path or (output_dir and '..' in output_dir):
            return {"success": False, "error": "Path traversal not allowed"}

        full_input = os.path.join(self.VIDEODATA_BASE, input_path)

        if not os.path.exists(full_input):
            return {"success": False, "error": f"Input file not found: {input_path}"}

        # Determine output directory
        if output_dir:
            full_output_dir = os.path.join(self.VIDEODATA_BASE, output_dir)
        else:
            full_output_dir = os.path.dirname(full_input)

        os.makedirs(full_output_dir, mode=0o755, exist_ok=True)

        try:
            # Get video info
            info = await asyncio.to_thread(self.ffmpeg.get_video_info, full_input)
            width, height = info['width'], info['height']
            duration = info['duration']
            fps = info['fps'] or 30

            # Calculate crop parameters
            crop_params = self.calculate_crop_params(width, height)

            # Generate output filename
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            ext = os.path.splitext(input_path)[1]
            method_suffix = "center" if method == CropMethod.CENTER else "facetrack"
            output_name = f"{base_name}_vertical_{method_suffix}_{output_size}{ext}"
            output_path = os.path.join(full_output_dir, output_name)
            relative_output = os.path.relpath(output_path, self.VIDEODATA_BASE)

            # Notify start
            if progress_callback:
                await progress_callback("vertical_started", {
                    "input": input_path,
                    "output": relative_output,
                    "method": method.value,
                    "output_size": output_size,
                    "source_resolution": f"{width}x{height}",
                    "crop_window": f"{crop_params.crop_w}x{crop_params.crop_h}",
                    "duration": round(duration, 2)
                })

            # Determine crop_x based on method
            if method == CropMethod.CENTER:
                # Apply center offset (percentage of max_x range)
                # offset -50 = full left, 0 = center, +50 = full right
                offset_clamped = max(-50, min(50, center_offset))
                offset_pixels = int((offset_clamped / 100.0) * crop_params.max_x)
                crop_x = crop_params.center_x + offset_pixels
                # Clamp to valid range
                crop_x = max(0, min(crop_params.max_x, crop_x))
            else:
                # Face tracking - analyze video
                positions = await self.analyze_video_faces(
                    full_input, crop_params, fps, duration, progress_callback
                )
                # For now, use average position (TODO: implement segment-based encoding)
                crop_x = int(np.mean(positions)) if positions else crop_params.center_x

            # Encode vertical video
            if progress_callback:
                await progress_callback("vertical_encoding", {
                    "progress": 0,
                    "crop_x": crop_x
                })

            # Get event loop for thread-safe callback
            loop = asyncio.get_running_loop()
            last_progress = [0]

            def encoding_progress(percent):
                if percent - last_progress[0] >= 5:  # Report every 5%
                    last_progress[0] = percent
                    if progress_callback:
                        # Schedule coroutine in the event loop from thread
                        loop.call_soon_threadsafe(
                            lambda p=percent: asyncio.ensure_future(
                                progress_callback("vertical_encoding", {"progress": round(p, 1)})
                            )
                        )

            await asyncio.to_thread(
                self.ffmpeg.crop_and_scale_vertical_with_progress,
                full_input, output_path, crop_x,
                width, height, output_size, encoding_progress
            )

            # Get output file size
            file_size = os.path.getsize(output_path)

            result = {
                "success": True,
                "input": input_path,
                "output": relative_output,
                "method": method.value,
                "output_size": output_size,
                "crop_x": crop_x,
                "duration": round(duration, 2),
                "size_bytes": file_size
            }

            if progress_callback:
                await progress_callback("vertical_completed", result)

            return result

        except Exception as e:
            error_result = {
                "success": False,
                "input": input_path,
                "error": str(e)
            }

            if progress_callback:
                await progress_callback("vertical_error", error_result)

            return error_result

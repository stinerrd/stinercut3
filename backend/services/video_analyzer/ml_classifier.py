"""
ML Classifier service using neurostiner model.
Classifies video frames into skydiving categories.
"""
import numpy as np
import cv2
from typing import List, Optional, Callable, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
import asyncio

# Import from local neurostiner copy
from .neurostiner import load_model, CATEGORIES, INPUT_SIZE


@dataclass
class FrameClassification:
    """Classification result for a single frame."""
    timestamp: float
    category: str  # neurostiner category: boden, canopy, freefall, in_plane
    confidence: float
    probabilities: dict


@dataclass
class FrameData:
    """Raw frame data for batch processing."""
    video_id: str  # Identifier for the source video
    timestamp: float
    frame: np.ndarray  # Preprocessed frame ready for inference


class MLClassifier:
    """
    EfficientNetB0 classifier for skydiving frame classification.
    Wraps neurostiner model for video analysis.
    """

    def __init__(self):
        self._model = None

    def _ensure_loaded(self):
        """Lazy load model on first use."""
        if self._model is None:
            print("Loading neurostiner ML model...")
            self._model = load_model()
            print("ML model loaded successfully!")

    def classify_frame(self, frame: np.ndarray, timestamp: float) -> FrameClassification:
        """
        Classify a single OpenCV frame.

        Args:
            frame: OpenCV frame in BGR format (numpy array)
            timestamp: Timestamp in seconds

        Returns:
            FrameClassification with category, confidence, and probabilities
        """
        self._ensure_loaded()

        # Preprocess: BGR to RGB, resize, normalize
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_AREA)
        batch = np.expand_dims(resized.astype(np.float32), axis=0)

        # Predict
        predictions = self._model.predict(batch, verbose=0)[0]
        idx = np.argmax(predictions)

        return FrameClassification(
            timestamp=timestamp,
            category=CATEGORIES[idx],
            confidence=float(predictions[idx]),
            probabilities={cat: float(predictions[i]) for i, cat in enumerate(CATEGORIES)}
        )

    def classify_video(
        self,
        video_path: str,
        interval: float = 1.0,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[FrameClassification]:
        """
        Sample and classify frames from video.

        Args:
            video_path: Path to video file
            interval: Seconds between frame samples
            progress_callback: Optional callback(progress_percent, message)

        Returns:
            List of FrameClassification for each sampled frame
        """
        self._ensure_loaded()
        results = []

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        # Calculate sample timestamps
        timestamps = []
        t = 0.0
        while t < duration:
            timestamps.append(t)
            t += interval

        total_samples = len(timestamps)

        for i, timestamp in enumerate(timestamps):
            # Seek to frame
            frame_num = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if ret:
                classification = self.classify_frame(frame, timestamp)
                results.append(classification)

            # Progress callback
            if progress_callback:
                progress = int((i + 1) / total_samples * 100)
                progress_callback(progress, f"Classified frame at {timestamp:.1f}s")

        cap.release()
        return results

    async def classify_video_async(
        self,
        video_path: str,
        interval: float = 1.0,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[FrameClassification]:
        """
        Async version of classify_video for non-blocking operation.
        """
        return await asyncio.to_thread(
            self.classify_video,
            video_path,
            interval,
            progress_callback
        )

    def extract_frames_from_video(
        self,
        video_path: str,
        video_id: str,
        interval: float = 1.0
    ) -> List[FrameData]:
        """
        Extract and preprocess frames from a video without classification.

        Args:
            video_path: Path to video file
            video_id: Identifier for the video (used to map results back)
            interval: Seconds between frame samples

        Returns:
            List of FrameData with preprocessed frames
        """
        frames = []

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return frames

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        # Calculate sample timestamps
        t = 0.0
        while t < duration:
            frame_num = int(t * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()

            if ret:
                # Preprocess: BGR to RGB, resize
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                resized = cv2.resize(rgb, (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_AREA)
                frames.append(FrameData(
                    video_id=video_id,
                    timestamp=t,
                    frame=resized.astype(np.float32)
                ))
            t += interval

        cap.release()
        return frames

    def _extract_frame_at_timestamp(
        self,
        cap: cv2.VideoCapture,
        fps: float,
        timestamp: float,
        video_id: str
    ) -> Optional[FrameData]:
        """Extract and preprocess a single frame at given timestamp."""
        frame_num = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()

        if ret:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (INPUT_SIZE, INPUT_SIZE), interpolation=cv2.INTER_AREA)
            return FrameData(
                video_id=video_id,
                timestamp=timestamp,
                frame=resized.astype(np.float32)
            )
        return None

    def classify_video_adaptive(
        self,
        video_path: str,
        coarse_interval: float = 10.0,
        fine_interval: float = 1.0
    ) -> List[FrameClassification]:
        """
        Classify video using adaptive sampling strategy.

        First pass: Sample at coarse_interval (e.g., every 10 seconds)
        Second pass: Refine around category transitions with fine_interval (e.g., every 1 second)

        Args:
            video_path: Path to video file
            coarse_interval: Seconds between coarse samples (default 10s)
            fine_interval: Seconds between fine samples around transitions (default 1s)

        Returns:
            List of FrameClassification sorted by timestamp
        """
        self._ensure_loaded()

        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        if duration <= 0:
            cap.release()
            return []

        # Phase 1: Coarse sampling
        coarse_timestamps = []
        t = 0.0
        while t < duration:
            coarse_timestamps.append(t)
            t += coarse_interval

        # Always include the last frame
        if coarse_timestamps[-1] < duration - 1:
            coarse_timestamps.append(min(duration - 0.1, coarse_timestamps[-1] + coarse_interval))

        # Extract and classify coarse frames
        coarse_frames = []
        for ts in coarse_timestamps:
            frame_data = self._extract_frame_at_timestamp(cap, fps, ts, "coarse")
            if frame_data:
                coarse_frames.append(frame_data)

        if not coarse_frames:
            cap.release()
            return []

        # Batch classify coarse frames
        batch_array = np.stack([f.frame for f in coarse_frames], axis=0)
        predictions = self._model.predict(batch_array, verbose=0)

        coarse_results = []
        for i, frame_data in enumerate(coarse_frames):
            pred = predictions[i]
            idx = np.argmax(pred)
            coarse_results.append(FrameClassification(
                timestamp=frame_data.timestamp,
                category=CATEGORIES[idx],
                confidence=float(pred[idx]),
                probabilities={cat: float(pred[j]) for j, cat in enumerate(CATEGORIES)}
            ))

        # Phase 2: Find transitions and refine
        transitions = []
        for i in range(1, len(coarse_results)):
            if coarse_results[i].category != coarse_results[i-1].category:
                # Found a transition between coarse_results[i-1] and coarse_results[i]
                transitions.append((coarse_results[i-1].timestamp, coarse_results[i].timestamp))

        # Collect fine-grained timestamps around transitions
        fine_timestamps = set()
        for start_ts, end_ts in transitions:
            # Sample at fine_interval between the two coarse points
            t = start_ts + fine_interval
            while t < end_ts:
                fine_timestamps.add(t)
                t += fine_interval

        # Remove timestamps we already have
        existing_timestamps = {r.timestamp for r in coarse_results}
        fine_timestamps = fine_timestamps - existing_timestamps

        # Extract and classify fine frames
        fine_results = []
        if fine_timestamps:
            fine_frames = []
            for ts in sorted(fine_timestamps):
                frame_data = self._extract_frame_at_timestamp(cap, fps, ts, "fine")
                if frame_data:
                    fine_frames.append(frame_data)

            if fine_frames:
                batch_array = np.stack([f.frame for f in fine_frames], axis=0)
                predictions = self._model.predict(batch_array, verbose=0)

                for i, frame_data in enumerate(fine_frames):
                    pred = predictions[i]
                    idx = np.argmax(pred)
                    fine_results.append(FrameClassification(
                        timestamp=frame_data.timestamp,
                        category=CATEGORIES[idx],
                        confidence=float(pred[idx]),
                        probabilities={cat: float(pred[j]) for j, cat in enumerate(CATEGORIES)}
                    ))

        cap.release()

        # Combine and sort results
        all_results = coarse_results + fine_results
        all_results.sort(key=lambda x: x.timestamp)

        return all_results

    def classify_batch(
        self,
        frames: List[FrameData],
        batch_size: int = 32,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, List[FrameClassification]]:
        """
        Classify multiple frames in batches.

        Args:
            frames: List of FrameData from multiple videos
            batch_size: Number of frames per inference batch
            progress_callback: Optional callback(processed, total)

        Returns:
            Dict mapping video_id to list of FrameClassification
        """
        self._ensure_loaded()

        if not frames:
            return {}

        # Results grouped by video_id
        results: Dict[str, List[FrameClassification]] = {}
        total = len(frames)

        # Process in batches
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch_frames = frames[batch_start:batch_end]

            # Stack frames into batch array
            batch_array = np.stack([f.frame for f in batch_frames], axis=0)

            # Run inference on batch
            predictions = self._model.predict(batch_array, verbose=0)

            # Process results
            for i, frame_data in enumerate(batch_frames):
                pred = predictions[i]
                idx = np.argmax(pred)

                classification = FrameClassification(
                    timestamp=frame_data.timestamp,
                    category=CATEGORIES[idx],
                    confidence=float(pred[idx]),
                    probabilities={cat: float(pred[j]) for j, cat in enumerate(CATEGORIES)}
                )

                if frame_data.video_id not in results:
                    results[frame_data.video_id] = []
                results[frame_data.video_id].append(classification)

            if progress_callback:
                progress_callback(batch_end, total)

        # Sort results by timestamp for each video
        for video_id in results:
            results[video_id].sort(key=lambda x: x.timestamp)

        return results


# Singleton instance for reuse
_classifier_instance: Optional[MLClassifier] = None


def get_classifier() -> MLClassifier:
    """Get or create singleton MLClassifier instance."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = MLClassifier()
    return _classifier_instance

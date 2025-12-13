"""
Segment Detector service.
Detects segment boundaries from frame classifications.
"""
from typing import List, Tuple
from dataclasses import dataclass
from collections import Counter

from .ml_classifier import FrameClassification


@dataclass
class VideoSegment:
    """Detected segment within a video."""
    start_time: float
    end_time: float
    classification: str  # Our classification: qr_code, ground_before, flight, freefall, canopy, ground_after, unknown
    confidence: float
    sequence_order: int


class SegmentDetector:
    """
    Detects segment boundaries from frame classifications.
    Maps neurostiner categories to our classifications and handles boundary detection.
    """

    # Neurostiner category to our classification mapping
    CATEGORY_MAP = {
        'freefall': 'freefall',
        'canopy': 'canopy',
        'in_plane': 'flight',
        'boden': 'ground',  # Will be refined to ground_before or ground_after
    }

    def __init__(self, smoothing_window: int = 3, min_segment_duration: float = 3.0):
        """
        Args:
            smoothing_window: Number of frames for majority vote smoothing
            min_segment_duration: Minimum segment duration in seconds (shorter segments are merged)
        """
        self.smoothing_window = smoothing_window
        self.min_segment_duration = min_segment_duration

    def detect_segments(
        self,
        classifications: List[FrameClassification],
        qr_end_time: float = None
    ) -> Tuple[List[VideoSegment], str]:
        """
        Detect segment boundaries from frame classifications.

        Args:
            classifications: List of frame classifications from ML classifier
            qr_end_time: If QR was detected, the end time of QR segment

        Returns:
            Tuple of (list of VideoSegment, dominant_classification)
        """
        if not classifications:
            return [], 'unknown'

        # Apply smoothing to reduce noise
        smoothed = self._apply_smoothing(classifications)

        # Map categories
        mapped = self._map_categories(smoothed)

        # Detect boundaries
        raw_segments = self._detect_boundaries(mapped)

        # Merge short segments
        merged = self._merge_short_segments(raw_segments)

        # Refine ground classifications (before/after freefall)
        refined = self._refine_ground_classifications(merged)

        # Add QR segment if detected
        if qr_end_time and qr_end_time > 0:
            refined = self._add_qr_segment(refined, qr_end_time)

        # Assign sequence orders
        for i, seg in enumerate(refined):
            seg.sequence_order = i

        # Calculate dominant classification
        dominant = self._calculate_dominant(refined)

        return refined, dominant

    def _apply_smoothing(self, classifications: List[FrameClassification]) -> List[FrameClassification]:
        """Apply majority vote smoothing to reduce noise."""
        if len(classifications) <= self.smoothing_window:
            return classifications

        smoothed = []
        half_window = self.smoothing_window // 2

        for i, clf in enumerate(classifications):
            # Get window around current frame
            start = max(0, i - half_window)
            end = min(len(classifications), i + half_window + 1)
            window = classifications[start:end]

            # Majority vote
            categories = [c.category for c in window]
            most_common = Counter(categories).most_common(1)[0][0]

            # Keep original if no clear majority
            if most_common == clf.category:
                smoothed.append(clf)
            else:
                # Create new classification with smoothed category
                smoothed.append(FrameClassification(
                    timestamp=clf.timestamp,
                    category=most_common,
                    confidence=clf.confidence,
                    probabilities=clf.probabilities
                ))

        return smoothed

    def _map_categories(self, classifications: List[FrameClassification]) -> List[Tuple[float, str, float]]:
        """Map neurostiner categories to our classifications."""
        mapped = []
        for clf in classifications:
            our_category = self.CATEGORY_MAP.get(clf.category, 'unknown')
            mapped.append((clf.timestamp, our_category, clf.confidence))
        return mapped

    def _detect_boundaries(self, mapped: List[Tuple[float, str, float]]) -> List[VideoSegment]:
        """Detect segment boundaries from mapped classifications."""
        if not mapped:
            return []

        segments = []
        current_start = mapped[0][0]
        current_category = mapped[0][1]
        current_confidences = [mapped[0][2]]

        for i in range(1, len(mapped)):
            timestamp, category, confidence = mapped[i]

            if category != current_category:
                # End current segment
                avg_confidence = sum(current_confidences) / len(current_confidences)
                segments.append(VideoSegment(
                    start_time=current_start,
                    end_time=timestamp,
                    classification=current_category,
                    confidence=avg_confidence,
                    sequence_order=0
                ))
                # Start new segment
                current_start = timestamp
                current_category = category
                current_confidences = [confidence]
            else:
                current_confidences.append(confidence)

        # Add final segment
        if mapped:
            avg_confidence = sum(current_confidences) / len(current_confidences)
            segments.append(VideoSegment(
                start_time=current_start,
                end_time=mapped[-1][0] + 1.0,  # Extend to cover last frame
                classification=current_category,
                confidence=avg_confidence,
                sequence_order=0
            ))

        return segments

    def _merge_short_segments(self, segments: List[VideoSegment]) -> List[VideoSegment]:
        """Merge segments shorter than min_segment_duration."""
        if len(segments) <= 1:
            return segments

        merged = []
        i = 0

        while i < len(segments):
            seg = segments[i]
            duration = seg.end_time - seg.start_time

            if duration < self.min_segment_duration and i > 0 and i < len(segments) - 1:
                # Short segment - merge with neighbor that has same classification
                prev_seg = merged[-1] if merged else None
                next_seg = segments[i + 1] if i + 1 < len(segments) else None

                if prev_seg and prev_seg.classification == seg.classification:
                    # Extend previous segment
                    prev_seg.end_time = seg.end_time
                elif next_seg and next_seg.classification == seg.classification:
                    # Will be absorbed by next segment
                    segments[i + 1] = VideoSegment(
                        start_time=seg.start_time,
                        end_time=next_seg.end_time,
                        classification=next_seg.classification,
                        confidence=(seg.confidence + next_seg.confidence) / 2,
                        sequence_order=0
                    )
                elif prev_seg:
                    # Merge with previous (different classification)
                    prev_seg.end_time = seg.end_time
                else:
                    merged.append(seg)
            else:
                # Segment is long enough or at boundary
                if merged and merged[-1].classification == seg.classification:
                    # Same classification - extend previous
                    merged[-1].end_time = seg.end_time
                    merged[-1].confidence = (merged[-1].confidence + seg.confidence) / 2
                else:
                    merged.append(seg)

            i += 1

        return merged

    def _refine_ground_classifications(self, segments: List[VideoSegment]) -> List[VideoSegment]:
        """Refine 'ground' to 'ground_before' or 'ground_after' based on jump sequence."""
        # Ground after freefall OR canopy is ground_after
        # (canopy always comes after freefall in skydiving)
        jump_occurred = False

        for seg in segments:
            if seg.classification in ('freefall', 'canopy'):
                jump_occurred = True
            elif seg.classification == 'ground':
                if jump_occurred:
                    seg.classification = 'ground_after'
                else:
                    seg.classification = 'ground_before'

        return segments

    def _add_qr_segment(self, segments: List[VideoSegment], qr_end_time: float) -> List[VideoSegment]:
        """Add QR code segment at the beginning."""
        if not segments:
            return [VideoSegment(
                start_time=0,
                end_time=qr_end_time,
                classification='qr_code',
                confidence=1.0,
                sequence_order=0
            )]

        # Adjust first segment if it overlaps with QR
        if segments[0].start_time < qr_end_time:
            if segments[0].end_time <= qr_end_time:
                # First segment is entirely within QR period - replace it
                segments[0].classification = 'qr_code'
                segments[0].start_time = 0
            else:
                # Split first segment
                first_seg = segments[0]
                qr_segment = VideoSegment(
                    start_time=0,
                    end_time=qr_end_time,
                    classification='qr_code',
                    confidence=1.0,
                    sequence_order=0
                )
                first_seg.start_time = qr_end_time
                segments.insert(0, qr_segment)
        else:
            # Insert QR segment at beginning
            qr_segment = VideoSegment(
                start_time=0,
                end_time=qr_end_time,
                classification='qr_code',
                confidence=1.0,
                sequence_order=0
            )
            segments.insert(0, qr_segment)

        return segments

    def _calculate_dominant(self, segments: List[VideoSegment]) -> str:
        """Calculate dominant classification based on total duration."""
        if not segments:
            return 'unknown'

        # Priority: freefall > canopy > flight > ground_before > ground_after > qr_code
        priority = {
            'freefall': 6,
            'canopy': 5,
            'flight': 4,
            'ground_before': 3,
            'ground_after': 2,
            'qr_code': 1,
            'unknown': 0
        }

        # Calculate total duration per classification
        durations = {}
        for seg in segments:
            duration = seg.end_time - seg.start_time
            durations[seg.classification] = durations.get(seg.classification, 0) + duration

        # Find classification with highest duration among high-priority ones
        best_classification = 'unknown'
        best_duration = 0

        for classification, duration in durations.items():
            # Prefer higher priority classifications even with shorter duration
            if priority.get(classification, 0) > priority.get(best_classification, 0):
                best_classification = classification
                best_duration = duration
            elif priority.get(classification, 0) == priority.get(best_classification, 0):
                if duration > best_duration:
                    best_classification = classification
                    best_duration = duration

        return best_classification

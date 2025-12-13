"""
Video Analyzer orchestrator service.
Main service that coordinates the full analysis pipeline.
"""
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Any, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from PIL import Image
from pyzbar.pyzbar import decode
import io

from sqlalchemy.orm import Session

from database import SessionLocal
from services.ffmpeg_service import FFmpegService
from models.import_batch import ImportBatch
from models.video_file import VideoFile
from models.video_file_segment import VideoFileSegment

from .ml_classifier import MLClassifier, FrameData, FrameClassification, get_classifier
from .segment_detector import SegmentDetector, VideoSegment
from .jump_resolver import JumpResolver, ResolutionResult


VIDEODATA_PATH = os.getenv("VIDEODATA_PATH", "/videodata")
DEFAULT_WORKERS = int(os.getenv("ANALYZER_WORKERS", "4"))


class VideoAnalyzer:
    """
    Main orchestrator for video analysis pipeline.
    Coordinates QR detection, ML classification, and jump resolution.
    """

    def __init__(
        self,
        db: Session,
        workers: int = DEFAULT_WORKERS,
        batch_size: int = 64,
        adaptive: bool = True,
        coarse_interval: float = 10.0,
        fine_interval: float = 1.0
    ):
        self.db = db
        self.workers = workers
        self.batch_size = batch_size
        self.adaptive = adaptive
        self.coarse_interval = coarse_interval
        self.fine_interval = fine_interval
        self.ffmpeg = FFmpegService()
        self.classifier = get_classifier()
        self.segment_detector = SegmentDetector()
        self.jump_resolver = JumpResolver(os.path.join(VIDEODATA_PATH, "input"), db)
        self._progress_lock = threading.Lock()

    async def analyze_folder(
        self,
        folder_path: str,
        progress_callback: Optional[Callable[[str, dict], Any]] = None
    ) -> ImportBatch:
        """
        Analyze all video files in a folder.

        Args:
            folder_path: Relative path to folder (e.g., "input/abc123")
            progress_callback: Optional async callback(event_type, data)

        Returns:
            ImportBatch with analysis results
        """
        # Extract folder UUID from path
        folder_uuid = Path(folder_path).name
        abs_folder_path = os.path.join(VIDEODATA_PATH, folder_path)

        # Validate folder exists
        if not os.path.isdir(abs_folder_path):
            raise ValueError(f"Folder not found: {folder_path}")

        # Phase 1: Batch Initialization
        batch = await self._init_batch(folder_uuid, abs_folder_path)

        if progress_callback:
            await progress_callback("analysis_started", {
                "batch_id": batch.uuid,
                "total_files": batch.total_files
            })

        # Get all video files
        video_files = self._get_video_files(abs_folder_path)

        if not video_files:
            batch.status = 'error'
            batch.error_message = 'No video files found in folder'
            self.db.commit()
            return batch

        # Create VideoFile records
        file_records = await self._create_file_records(batch, video_files, folder_uuid, abs_folder_path)

        # Phase 2: Per-File Analysis (Parallel)
        results = await self._analyze_files_parallel(
            batch.uuid,
            video_files,
            [r.id for r in file_records],
            progress_callback
        )

        # Update batch with results
        batch.analyzed_files = results['success_count']
        self.db.commit()

        # Refresh file records from DB to get updated data
        file_records = self.db.query(VideoFile).filter(
            VideoFile.import_folder_uuid == folder_uuid
        ).all()

        # Phase 3: Jump Resolution
        resolution = await self._resolve_jumps(batch, file_records)

        # Update batch with resolution info
        batch.detected_qr_count = len(resolution.detected_qr_uuids)
        batch.detected_freefall_count = resolution.freefall_count

        # Phase 4: File Organization (if resolved)
        if resolution.status == 'resolved':
            resolved_folder_name = self.jump_resolver.execute_resolution(resolution, folder_uuid)
            if resolved_folder_name:
                batch.status = 'resolved'
                batch.resolution_type = resolution.resolution_type
                # Store resolved folder name for organize signal
                batch.resolved_folder_name = resolved_folder_name
                # Update file records with new paths
                for record in file_records:
                    self.db.add(record)
            else:
                batch.status = 'error'
                batch.error_message = 'Failed to move files to workload folders'
        else:
            batch.status = 'needs_manual'
            batch.resolution_type = resolution.resolution_type
            batch.error_message = resolution.message

        self.db.commit()

        if progress_callback:
            await progress_callback("batch_completed", {
                "batch_id": batch.uuid,
                "status": batch.status,
                "resolution_type": batch.resolution_type,
                "total": batch.total_files,
                "success": batch.analyzed_files,
                "errors": batch.total_files - batch.analyzed_files,
                "detected_qr_count": batch.detected_qr_count,
                "detected_freefall_count": batch.detected_freefall_count
            })

        return batch

    async def _init_batch(self, folder_uuid: str, abs_folder_path: str) -> ImportBatch:
        """Initialize import batch record."""
        # Check if batch already exists
        existing = self.db.query(ImportBatch).filter(ImportBatch.uuid == folder_uuid).first()
        if existing:
            # Reset for re-analysis
            existing.status = 'analyzing'
            existing.analyzed_files = 0
            existing.error_message = None
            self.db.commit()
            return existing

        # Count video files
        video_files = self._get_video_files(abs_folder_path)

        batch = ImportBatch(
            uuid=folder_uuid,
            total_files=len(video_files),
            analyzed_files=0,
            status='analyzing'
        )
        self.db.add(batch)
        self.db.commit()
        return batch

    def _get_video_files(self, folder_path: str) -> List[str]:
        """Get list of video files in folder (including subdirectories)."""
        video_extensions = {'.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV'}
        # Skip LRV files (GoPro low-res proxy files)
        files = []

        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                ext = os.path.splitext(filename)[1]
                # Skip hidden files (._* macOS metadata)
                if filename.startswith('._'):
                    continue
                if ext in video_extensions:
                    files.append(os.path.join(root, filename))

        # Sort by filename (usually chronological for GoPro)
        files.sort()
        return files

    async def _create_file_records(
        self,
        batch: ImportBatch,
        video_files: List[str],
        folder_uuid: str,
        abs_folder_path: str
    ) -> List[VideoFile]:
        """Create VideoFile records for all files."""
        records = []

        for file_path in video_files:
            filename = os.path.basename(file_path)
            # Get relative path from import folder
            rel_path = os.path.relpath(file_path, os.path.join(VIDEODATA_PATH, "input"))
            file_uuid = str(uuid.uuid4())

            record = VideoFile(
                uuid=file_uuid,
                import_folder_uuid=folder_uuid,
                current_folder_uuid=folder_uuid,
                filepath=rel_path,
                original_filename=filename,
                status='pending',
                import_source='gopro'
            )
            self.db.add(record)
            records.append(record)

        self.db.commit()
        return records

    async def _analyze_files_parallel(
        self,
        batch_uuid: str,
        video_files: List[str],
        record_ids: List[int],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple video files in parallel.

        Uses adaptive sampling (coarse 10s, fine 1s around transitions) for efficiency.
        Each worker handles one video file completely.

        Args:
            batch_uuid: Batch UUID for progress reporting
            video_files: List of absolute file paths
            record_ids: List of VideoFile record IDs (parallel to video_files)
            progress_callback: Optional async callback for progress

        Returns:
            Dict with success_count and error_count
        """
        success_count = 0
        error_count = 0
        results_queue = []

        # Pre-load the ML model before starting threads
        self.classifier._ensure_loaded()

        def analyze_single_file(file_path: str, record_id: int) -> Dict[str, Any]:
            """Worker: Analyze a single video file completely."""
            db = SessionLocal()
            ffmpeg = FFmpegService()
            segment_detector = SegmentDetector()

            result = {
                'record_id': record_id,
                'filename': os.path.basename(file_path),
                'success': False,
                'classification': None,
                'segments_count': 0,
                'workload_uuid': None,
                'error': None
            }

            try:
                record = db.query(VideoFile).get(record_id)
                if not record:
                    result['error'] = 'Record not found'
                    return result

                record.status = 'analyzing'
                db.commit()

                # 1. Metadata Extraction
                try:
                    info = ffmpeg.get_video_info(file_path)
                    record.duration = info['duration']
                    record.width = info['width']
                    record.height = info['height']
                    record.fps = info['fps']
                    record.codec = info['codec']
                    record.file_size_bytes = os.path.getsize(file_path)

                    thumbnail_time = info['duration'] * 0.25
                    record.thumbnail = ffmpeg.extract_thumbnail_jpeg(file_path, thumbnail_time)
                except Exception as e:
                    print(f"Warning: Failed to extract metadata for {result['filename']}: {e}")

                # 2. QR Detection
                qr_result = self._detect_qr_sync(file_path, ffmpeg)
                if qr_result['success']:
                    record.qr_content = qr_result['qr_content']
                    record.detected_workload_uuid = self._parse_workload_uuid(qr_result['qr_content'])
                    result['workload_uuid'] = record.detected_workload_uuid

                # 3. Frame Classification (adaptive sampling)
                if self.adaptive:
                    classifications = self.classifier.classify_video_adaptive(
                        file_path,
                        coarse_interval=self.coarse_interval,
                        fine_interval=self.fine_interval
                    )
                else:
                    classifications = self.classifier.classify_video(
                        file_path,
                        interval=self.fine_interval
                    )

                # 4. Segment Detection
                qr_end_time = qr_result.get('frame_timestamp', 0) + 2 if qr_result['success'] else None
                segments, dominant = segment_detector.detect_segments(classifications, qr_end_time)

                # Save segments
                for seg in segments:
                    segment_record = VideoFileSegment(
                        uuid=str(uuid.uuid4()),
                        video_file_id=record.id,
                        start_time=seg.start_time,
                        end_time=seg.end_time,
                        classification=seg.classification,
                        confidence=seg.confidence,
                        sequence_order=seg.sequence_order
                    )
                    db.add(segment_record)

                # Update record
                record.dominant_classification = dominant
                if classifications:
                    record.classification_confidence = sum(c.confidence for c in classifications) / len(classifications)

                record.status = 'analyzed'
                db.commit()

                result['success'] = True
                result['classification'] = dominant
                result['segments_count'] = len(segments)

            except Exception as e:
                result['error'] = str(e)
                try:
                    record = db.query(VideoFile).get(record_id)
                    if record:
                        record.status = 'error'
                        record.error_message = str(e)
                        db.commit()
                except:
                    pass
            finally:
                db.close()

            return result

        # Run analysis in thread pool
        print(f"Analyzing {len(video_files)} videos with adaptive sampling (coarse={self.coarse_interval}s, fine={self.fine_interval}s)...")

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            future_to_file = {
                executor.submit(analyze_single_file, fp, rid): (fp, rid)
                for fp, rid in zip(video_files, record_ids)
            }

            for future in as_completed(future_to_file):
                result = future.result()

                if result['success']:
                    success_count += 1
                    if progress_callback:
                        await progress_callback("file_analyzed", {
                            "batch_id": batch_uuid,
                            "filename": result['filename'],
                            "dominant_classification": result['classification'],
                            "segments_count": result['segments_count'],
                            "workload_uuid": result.get('workload_uuid')
                        })
                else:
                    error_count += 1
                    print(f"Error analyzing {result['filename']}: {result.get('error')}")

        return {
            'success_count': success_count,
            'error_count': error_count
        }

    def _detect_qr_sync(self, video_path: str, ffmpeg: FFmpegService) -> dict:
        """Synchronous QR detection for use in thread pool."""
        try:
            duration = ffmpeg.get_duration(video_path)
        except ValueError:
            return {"success": False, "qr_content": None, "frame_timestamp": None}

        timestamps = [0.0, 1.0, 2.0, 5.0]
        if duration > 10:
            timestamps.extend([duration * 0.10])
        timestamps = [t for t in timestamps if t < min(duration, 10)]

        for timestamp in timestamps:
            try:
                frame_bytes = ffmpeg.extract_frame(video_path, timestamp)
                qr_content = self._detect_qr_in_image(frame_bytes)
                if qr_content:
                    return {
                        "success": True,
                        "qr_content": qr_content,
                        "frame_timestamp": timestamp
                    }
            except Exception:
                continue

        return {"success": False, "qr_content": None, "frame_timestamp": None}

    async def _analyze_file(
        self,
        record: VideoFile,
        file_path: str,
        progress_callback: Optional[Callable] = None
    ):
        """Analyze a single video file (legacy sequential method)."""
        record.status = 'analyzing'
        self.db.commit()

        # 2a. Metadata Extraction
        try:
            info = self.ffmpeg.get_video_info(file_path)
            record.duration = info['duration']
            record.width = info['width']
            record.height = info['height']
            record.fps = info['fps']
            record.codec = info['codec']

            # Get file size
            record.file_size_bytes = os.path.getsize(file_path)

            # Extract thumbnail at 25%
            thumbnail_time = info['duration'] * 0.25
            record.thumbnail = self.ffmpeg.extract_thumbnail_jpeg(file_path, thumbnail_time)

        except Exception as e:
            print(f"Warning: Failed to extract metadata: {e}")

        # 2b. QR Detection (first 10 seconds)
        qr_result = await self._detect_qr(file_path)
        if qr_result['success']:
            record.qr_content = qr_result['qr_content']
            # Parse workload UUID from "Stinercut: {uuid}" format
            record.detected_workload_uuid = self._parse_workload_uuid(qr_result['qr_content'])

        # 2c. Frame Classification (Neurostiner)
        # Note: progress_callback not used here since classify_video_async runs in a thread
        classifications = await self.classifier.classify_video_async(
            file_path,
            interval=1.0,
            progress_callback=None
        )

        # 2d. Segment Boundary Detection
        qr_end_time = qr_result.get('frame_timestamp', 0) + 2 if qr_result['success'] else None
        segments, dominant = self.segment_detector.detect_segments(classifications, qr_end_time)

        # Save segments
        for seg in segments:
            segment_record = VideoFileSegment(
                uuid=str(uuid.uuid4()),
                video_file_id=record.id,
                start_time=seg.start_time,
                end_time=seg.end_time,
                classification=seg.classification,
                confidence=seg.confidence,
                sequence_order=seg.sequence_order
            )
            self.db.add(segment_record)

        # Update record with results
        record.dominant_classification = dominant
        if classifications:
            record.classification_confidence = sum(c.confidence for c in classifications) / len(classifications)

        record.status = 'analyzed'
        self.db.commit()

    async def _detect_qr(self, video_path: str) -> dict:
        """Detect QR code in video (first 10 seconds)."""
        try:
            duration = self.ffmpeg.get_duration(video_path)
        except ValueError:
            return {"success": False, "qr_content": None, "frame_timestamp": None}

        # Only scan first 10 seconds
        timestamps = [0.0, 1.0, 2.0, 5.0]
        if duration > 10:
            timestamps.extend([duration * 0.10])
        timestamps = [t for t in timestamps if t < min(duration, 10)]

        for timestamp in timestamps:
            try:
                frame_bytes = self.ffmpeg.extract_frame(video_path, timestamp)
                qr_content = self._detect_qr_in_image(frame_bytes)
                if qr_content:
                    return {
                        "success": True,
                        "qr_content": qr_content,
                        "frame_timestamp": timestamp
                    }
            except Exception:
                continue

        return {"success": False, "qr_content": None, "frame_timestamp": None}

    def _detect_qr_in_image(self, image_bytes: bytes) -> Optional[str]:
        """Detect QR code in image bytes."""
        try:
            image = Image.open(io.BytesIO(image_bytes))
            decoded = decode(image)
            if decoded:
                return decoded[0].data.decode('utf-8')
            return None
        except Exception:
            return None

    def _parse_workload_uuid(self, qr_content: str) -> Optional[str]:
        """Parse workload UUID from QR content."""
        if not qr_content:
            return None

        # Format: "Stinercut: {uuid}"
        match = re.match(r'^Stinercut:\s*([a-f0-9-]+)$', qr_content, re.IGNORECASE)
        if match:
            return match.group(1)

        # Try to extract any UUID-like string
        uuid_pattern = r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
        match = re.search(uuid_pattern, qr_content, re.IGNORECASE)
        if match:
            return match.group(0)

        return None

    async def _resolve_jumps(
        self,
        batch: ImportBatch,
        files: List[VideoFile]
    ) -> ResolutionResult:
        """Resolve jump assignments."""
        return self.jump_resolver.resolve_jumps(files)

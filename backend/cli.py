#!/usr/bin/env python3
"""
CLI commands for Stinercut backend.
Run with: python cli.py <command> [options]
"""
import argparse
import asyncio
import sys
import time

from database import SessionLocal
from services.video_analyzer import VideoAnalyzer
from services.video_splitter import VideoSplitterService
from services.video_slowmo import VideoSlowmoService
from services.video_transition import VideoTransitionService
from services.animated_pax_service import AnimatedPaxService


def run_detection(
    folder_path: str,
    verbose: bool = False,
    workers: int = 4,
    coarse_interval: float = 10.0,
    fine_interval: float = 1.0,
    no_adaptive: bool = False
):
    """
    Run video detection on a folder.

    Args:
        folder_path: Relative path to folder (e.g., "input/abc123")
        verbose: Show detailed progress
        workers: Number of parallel workers
        coarse_interval: Seconds between coarse samples (adaptive mode)
        fine_interval: Seconds between fine samples (around transitions)
        no_adaptive: Disable adaptive sampling, use fine_interval for all frames
    """
    print(f"Starting video detection for: {folder_path}")
    print(f"Using {workers} parallel workers")
    if no_adaptive:
        print(f"Sampling: every {fine_interval}s (adaptive disabled)")
    else:
        print(f"Adaptive sampling: coarse {coarse_interval}s, fine {fine_interval}s around transitions")
    print("-" * 50)
    start_time = time.time()

    async def progress_callback(event_type: str, data: dict):
        """Print progress updates."""
        if event_type == "analysis_started":
            print(f"Analyzing batch: {data.get('batch_id')}")
            print(f"Total files: {data.get('total_files')}")

        elif event_type == "file_analyzed":
            filename = data.get('filename', 'unknown')
            classification = data.get('dominant_classification', 'unknown')
            segments = data.get('segments_count', 0)
            project = data.get('project_uuid', 'none')
            print(f"  ✓ {filename}: {classification} ({segments} segments)")
            if project and project != 'none':
                print(f"    QR detected: {project}")

        elif event_type == "analysis_progress" and verbose:
            filename = data.get('filename', '')
            progress = data.get('progress', 0)
            print(f"    [{progress}%] Classifying {filename}...", end='\r')

        elif event_type == "batch_completed":
            print("-" * 50)
            print(f"Status: {data.get('status')}")
            print(f"Resolution: {data.get('resolution_type')}")
            print(f"Files: {data.get('success')}/{data.get('total')}")
            print(f"QR codes detected: {data.get('detected_qr_count')}")
            print(f"Freefalls detected: {data.get('detected_freefall_count')}")
            if data.get('errors', 0) > 0:
                print(f"Errors: {data.get('errors')}")

    async def run():
        db = SessionLocal()
        try:
            analyzer = VideoAnalyzer(
                db,
                workers=workers,
                adaptive=not no_adaptive,
                coarse_interval=coarse_interval,
                fine_interval=fine_interval
            )
            batch = await analyzer.analyze_folder(folder_path, progress_callback)
            # Extract values before session closes
            result = {
                'status': batch.status,
                'error_message': batch.error_message,
                'resolution_type': batch.resolution_type
            }
            return result
        finally:
            db.close()

    try:
        result = asyncio.run(run())
        elapsed = time.time() - start_time
        print("-" * 50)
        print(f"Completed in {elapsed:.1f} seconds")

        if result['status'] == 'resolved':
            print("Detection complete - files organized automatically")
            return 0
        elif result['status'] == 'needs_manual':
            print(f"Detection complete - manual intervention required")
            print(f"  Reason: {result['error_message']}")
            return 0
        else:
            print(f"Detection failed: {result['error_message']}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_split(
    input_path: str,
    timestamps: list,
    output_dir: str = None,
    verbose: bool = False
):
    """
    Split video at specified timestamps (snapped to nearest keyframes).

    Args:
        input_path: Relative path to video (e.g., "input/abc123/video.mp4")
        timestamps: List of split points in seconds
        output_dir: Output directory (optional, default: same as input)
        verbose: Show detailed progress
    """
    print(f"Splitting video: {input_path}")
    print(f"Split points: {timestamps}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print("-" * 50)
    start_time = time.time()

    async def progress_callback(event_type: str, data: dict):
        """Print progress updates."""
        if event_type == "split_started":
            print(f"Analyzing keyframes...")

        elif event_type == "keyframes_resolved":
            requested = data.get('requested', [])
            snapped = data.get('snapped', [])
            warnings = data.get('warnings', [])
            print(f"Requested timestamps: {requested}")
            print(f"Snapped to keyframes: {snapped}")
            for warning in warnings:
                print(f"  Warning: {warning}")

        elif event_type == "splitting_segment":
            segment = data.get('segment', 0)
            total = data.get('total', 0)
            start = data.get('start', 0)
            end = data.get('end', 0)
            output = data.get('output', '')
            if verbose:
                print(f"  [{segment}/{total}] {output} ({start:.2f}s - {end:.2f}s)")

        elif event_type == "split_completed":
            outputs = data.get('outputs', [])
            warnings = data.get('warnings', [])
            print("-" * 50)
            print(f"Split complete: {len(outputs)} segments created")
            for out in outputs:
                duration = out.get('duration', 0)
                size_mb = out.get('size_bytes', 0) / (1024 * 1024)
                print(f"  {out['path']} ({duration:.2f}s, {size_mb:.1f} MB)")

        elif event_type == "split_error":
            print(f"Error: {data.get('error', 'Unknown error')}")

    async def run():
        service = VideoSplitterService()
        return await service.split_video(
            input_path, timestamps, output_dir, progress_callback
        )

    try:
        result = asyncio.run(run())
        elapsed = time.time() - start_time

        if result['success']:
            print("-" * 50)
            print(f"Completed in {elapsed:.1f} seconds")
            return 0
        else:
            print(f"Split failed: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_slowmo(
    input_path: str,
    speed_factor: float = 0.5,
    output_dir: str = None,
    verbose: bool = False
):
    """
    Convert video to slow motion.

    Args:
        input_path: Relative path to video (e.g., "input/abc123/video.mp4")
        speed_factor: Speed multiplier (0.1 to 1.0, where 0.5 = 2x slower)
        output_dir: Output directory (optional, default: same as input)
        verbose: Show detailed progress
    """
    print(f"Converting to slow motion: {input_path}")
    print(f"Speed factor: {speed_factor}x ({1/speed_factor:.1f}x slower)")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print("-" * 50)
    start_time = time.time()

    async def progress_callback(event_type: str, data: dict):
        """Print progress updates."""
        if event_type == "slowmo_started":
            orig_dur = data.get('original_duration', 0)
            est_dur = data.get('estimated_output_duration', 0)
            print(f"Original duration: {orig_dur:.2f}s")
            print(f"Output duration: {est_dur:.2f}s")
            print("Encoding (this may take a while)...")

        elif event_type == "slowmo_completed":
            output = data.get('output', '')
            size_mb = data.get('size_bytes', 0) / (1024 * 1024)
            out_dur = data.get('output_duration', 0)
            print("-" * 50)
            print(f"Conversion complete!")
            print(f"  Output: {output}")
            print(f"  Duration: {out_dur:.2f}s")
            print(f"  Size: {size_mb:.1f} MB")

        elif event_type == "slowmo_error":
            print(f"Error: {data.get('error', 'Unknown error')}")

    async def run():
        service = VideoSlowmoService()
        return await service.convert_slowmo(
            input_path, speed_factor, output_dir, progress_callback
        )

    try:
        result = asyncio.run(run())
        elapsed = time.time() - start_time

        if result['success']:
            print("-" * 50)
            print(f"Completed in {elapsed:.1f} seconds")
            return 0
        else:
            print(f"Conversion failed: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_transition(
    file1_path: str,
    file2_path: str,
    transition_duration: float = 1.0,
    output_dir: str = None,
    keep_intermediate: bool = True,
    transition_only: bool = False,
    verbose: bool = False
):
    """
    Create fade-out-in transition between two videos.

    Args:
        file1_path: Relative path to first video
        file2_path: Relative path to second video
        transition_duration: Crossfade duration in seconds (default: 1.0)
        output_dir: Output directory (optional, default: same as file1)
        keep_intermediate: Keep intermediate segment files (default: True)
        transition_only: Only create transition segment, skip joining (default: False)
        verbose: Show detailed progress
    """
    print(f"Creating transition between:")
    print(f"  File 1: {file1_path}")
    print(f"  File 2: {file2_path}")
    print(f"Transition duration: {transition_duration}s")
    if transition_only:
        print("Mode: transition only (no final join)")
    if output_dir:
        print(f"Output directory: {output_dir}")
    if not keep_intermediate:
        print("Intermediate files will be deleted")
    print("-" * 50)
    start_time = time.time()

    async def progress_callback(event_type: str, data: dict):
        """Print progress updates."""
        if event_type == "transition_started":
            print(f"Starting transition process...")

        elif event_type == "extracting_part1":
            start = data.get('start', 0)
            end = data.get('end', 0)
            if verbose:
                print(f"  Extracting file1 part: {start:.2f}s - {end:.2f}s")

        elif event_type == "extracting_transition_clips":
            clip1 = data.get('clip1_range', [])
            clip2 = data.get('clip2_range', [])
            if verbose:
                print(f"  Extracting transition clips:")
                print(f"    File1: {clip1[0]:.2f}s - {clip1[1]:.2f}s")
                print(f"    File2: {clip2[0]:.2f}s - {clip2[1]:.2f}s")

        elif event_type == "extracting_part2":
            start = data.get('start', 0)
            end = data.get('end', 0)
            if verbose:
                print(f"  Extracting file2 part: {start:.2f}s - {end:.2f}s")

        elif event_type == "creating_crossfade":
            print(f"  Creating crossfade effect ({data.get('fade_duration')}s)...")

        elif event_type == "concatenating":
            print(f"  Concatenating {data.get('segments')} segments (stream copy)...")

        elif event_type == "transition_completed":
            output = data.get('output', '')
            size_mb = data.get('size_bytes', 0) / (1024 * 1024)
            out_dur = data.get('output_duration', 0)
            intermediate = data.get('intermediate_files', [])
            print("-" * 50)
            print(f"Transition complete!")
            print(f"  Output: {output}")
            print(f"  Duration: {out_dur:.2f}s")
            print(f"  Size: {size_mb:.1f} MB")
            if intermediate and verbose:
                print(f"  Intermediate files:")
                for f in intermediate:
                    print(f"    - {f}")

        elif event_type == "transition_error":
            print(f"Error: {data.get('error', 'Unknown error')}")

    async def run():
        service = VideoTransitionService()
        return await service.create_transition(
            file1_path, file2_path, output_dir,
            transition_duration, keep_intermediate, transition_only, progress_callback
        )

    try:
        result = asyncio.run(run())
        elapsed = time.time() - start_time

        if result['success']:
            print("-" * 50)
            print(f"Completed in {elapsed:.1f} seconds")
            return 0
        else:
            print(f"Transition failed: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_animated_pax_intro(
    name: str,
    template_id: int,
    output: str,
    duration: float = None,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    codec: str = "libx264",
    verbose: bool = False
):
    """
    Create animated PAX screen intro video.

    Uses FFmpeg overlay filters for high-performance animation.
    No audio - video only output.

    Args:
        name: Passenger name to display
        template_id: ID of splashscreen with embedded animation config
        output: Output directory path
        duration: Override template duration (optional)
        width: Video width (default: 1920)
        height: Video height (default: 1080)
        fps: Frame rate (default: 30)
        codec: Video codec (default: libx264)
        verbose: Show detailed progress
    """
    print(f"Creating animated PAX screen intro for: {name}")
    print(f"Template ID: {template_id}")
    print(f"Output: {output}")
    if duration:
        print(f"Duration override: {duration}s")
    print(f"Resolution: {width}x{height} @ {fps}fps")
    print("-" * 50)
    start_time = time.time()

    async def progress_callback(event_type: str, data: dict):
        """Print progress updates."""
        if event_type == "animated_pax_intro_started":
            print(f"Starting animated PAX intro creation...")

        elif event_type == "parsed_config":
            print(f"  Template: {data.get('template_name', 'unknown')}")
            print(f"  Animation: {data.get('animation_name', 'unknown')}")
            print(f"  Duration: {data.get('duration', 0)}s")
            print(f"  Layers: {data.get('layer_count', 0)}")

        elif event_type == "rendering_layer":
            layer_id = data.get('layer_id', '')
            progress = data.get('progress', 0)
            if verbose:
                print(f"  Rendering layer: {layer_id} ({progress*100:.0f}%)")

        elif event_type == "building_filter":
            layer_count = data.get('layer_count', 0)
            print(f"  Building FFmpeg filter for {layer_count} layers...")

        elif event_type == "encoding_video":
            print(f"  Encoding video...")

        elif event_type == "animated_pax_intro_completed":
            output_file = data.get('output_file', '')
            out_dur = data.get('duration', 0)
            print("-" * 50)
            print(f"Animated PAX intro complete!")
            print(f"  Output: {output_file}")
            print(f"  Duration: {out_dur}s")

        elif event_type == "animated_pax_intro_error":
            print(f"Error: {data.get('error', 'Unknown error')}")

    async def run():
        db = SessionLocal()
        try:
            service = AnimatedPaxService(db)
            return await service.create_animated_intro(
                template_id=template_id,
                pax_name=name,
                output_path=output,
                duration=duration,
                video_dimensions={
                    'width': width,
                    'height': height,
                    'fps': fps,
                    'codec': codec
                },
                progress_callback=progress_callback
            )
        finally:
            db.close()

    try:
        result = asyncio.run(run())
        elapsed = time.time() - start_time

        if result['success']:
            print("-" * 50)
            print(f"Completed in {elapsed:.1f} seconds")
            return 0
        else:
            print(f"Animated PAX intro failed: {result.get('error', 'Unknown error')}")
            return 1

    except Exception as e:
        print(f"Error: {e}")
        return 1


def list_pending(status: str = None):
    """List import batches with optional status filter."""
    from models import ImportBatch

    db = SessionLocal()
    try:
        query = db.query(ImportBatch)
        if status:
            query = query.filter(ImportBatch.status == status)
        query = query.order_by(ImportBatch.created_at.desc())

        batches = query.limit(20).all()

        if not batches:
            print("No batches found")
            return

        print(f"{'UUID':<36} {'Status':<15} {'Files':<10} {'QRs':<5} {'Falls':<6}")
        print("-" * 75)

        for batch in batches:
            print(f"{batch.uuid:<36} {batch.status:<15} "
                  f"{batch.analyzed_files}/{batch.total_files:<7} "
                  f"{batch.detected_qr_count or 0:<5} "
                  f"{batch.detected_freefall_count or 0:<6}")

    finally:
        db.close()


def clear_import(confirm: bool = False):
    """Clear all import-related database tables."""
    from models.video_file import VideoFile
    from models.video_file_segment import VideoFileSegment
    from models.import_batch import ImportBatch

    db = SessionLocal()
    try:
        # Count records before deletion
        segment_count = db.query(VideoFileSegment).count()
        file_count = db.query(VideoFile).count()
        batch_count = db.query(ImportBatch).count()

        print("Import-related tables:")
        print(f"  video_file_segment: {segment_count} records")
        print(f"  video_file: {file_count} records")
        print(f"  import_batch: {batch_count} records")
        print("-" * 50)

        if not confirm:
            print("Use --confirm to actually delete the records")
            return 0

        # Delete in order (segments first due to FK constraints)
        deleted_segments = db.query(VideoFileSegment).delete()
        deleted_files = db.query(VideoFile).delete()
        deleted_batches = db.query(ImportBatch).delete()

        db.commit()

        print("Deleted:")
        print(f"  video_file_segment: {deleted_segments} records")
        print(f"  video_file: {deleted_files} records")
        print(f"  import_batch: {deleted_batches} records")
        print("-" * 50)
        print("Import tables cleared successfully")
        return 0

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return 1
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="Stinercut CLI - Video detection and management"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # detect command
    detect_parser = subparsers.add_parser(
        "detect",
        help="Run video detection on a folder"
    )
    detect_parser.add_argument(
        "folder_path",
        help="Relative path to folder (e.g., input/abc123)"
    )
    detect_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )
    detect_parser.add_argument(
        "-w", "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    detect_parser.add_argument(
        "-c", "--coarse-interval",
        type=float,
        default=10.0,
        help="Coarse sampling interval in seconds (default: 10)"
    )
    detect_parser.add_argument(
        "-f", "--fine-interval",
        type=float,
        default=1.0,
        help="Fine sampling interval in seconds (default: 1)"
    )
    detect_parser.add_argument(
        "--no-adaptive",
        action="store_true",
        help="Disable adaptive sampling, sample every fine-interval"
    )

    # list command
    list_parser = subparsers.add_parser(
        "list",
        help="List import batches"
    )
    list_parser.add_argument(
        "--status",
        choices=["pending", "analyzing", "resolved", "needs_manual", "error"],
        help="Filter by status"
    )

    # clear-import command
    clear_parser = subparsers.add_parser(
        "clear-import",
        help="Clear import-related DB tables (video_file, video_file_segment, import_batch)"
    )
    clear_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Actually delete the records (without this flag, only shows counts)"
    )

    # split command
    split_parser = subparsers.add_parser(
        "split",
        help="Split video at keyframe timestamps"
    )
    split_parser.add_argument(
        "input_path",
        help="Relative path to video (e.g., input/abc123/video.mp4)"
    )
    split_parser.add_argument(
        "-t", "--timestamps",
        type=float,
        nargs="+",
        required=True,
        help="Split points in seconds (e.g., -t 30 60 90)"
    )
    split_parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as input)"
    )
    split_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    # slowmo command
    slowmo_parser = subparsers.add_parser(
        "slowmo",
        help="Convert video to slow motion"
    )
    slowmo_parser.add_argument(
        "input_path",
        help="Relative path to video (e.g., input/abc123/video.mp4)"
    )
    slowmo_parser.add_argument(
        "-s", "--speed",
        type=float,
        default=0.5,
        help="Speed factor (0.1-1.0, default: 0.5 = 2x slower)"
    )
    slowmo_parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as input)"
    )
    slowmo_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    # transition command
    transition_parser = subparsers.add_parser(
        "transition",
        help="Create fade transition between two videos"
    )
    transition_parser.add_argument(
        "file1_path",
        help="Relative path to first video"
    )
    transition_parser.add_argument(
        "file2_path",
        help="Relative path to second video"
    )
    transition_parser.add_argument(
        "-t", "--transition-duration",
        type=float,
        default=1.0,
        help="Crossfade duration in seconds (default: 1.0)"
    )
    transition_parser.add_argument(
        "-o", "--output-dir",
        help="Output directory (default: same as file1)"
    )
    transition_parser.add_argument(
        "--no-intermediate",
        action="store_true",
        help="Delete intermediate files after completion"
    )
    transition_parser.add_argument(
        "--transition-only",
        action="store_true",
        help="Only create transition segment, skip joining to final file"
    )
    transition_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    # animated-pax-intro command
    animated_pax_parser = subparsers.add_parser(
        "animated-pax-intro",
        help="Create animated PAX screen intro video (no audio)"
    )
    animated_pax_parser.add_argument(
        "--name",
        required=True,
        help="Passenger name to display"
    )
    animated_pax_parser.add_argument(
        "--template-id",
        type=int,
        required=True,
        help="ID of splashscreen with embedded animation config"
    )
    animated_pax_parser.add_argument(
        "--output",
        required=True,
        help="Output directory path"
    )
    animated_pax_parser.add_argument(
        "--duration",
        type=float,
        help="Override template duration in seconds (optional)"
    )
    animated_pax_parser.add_argument(
        "--width",
        type=int,
        default=1920,
        help="Video width (default: 1920)"
    )
    animated_pax_parser.add_argument(
        "--height",
        type=int,
        default=1080,
        help="Video height (default: 1080)"
    )
    animated_pax_parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frame rate (default: 30)"
    )
    animated_pax_parser.add_argument(
        "--codec",
        default="libx264",
        help="Video codec (default: libx264)"
    )
    animated_pax_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress"
    )

    args = parser.parse_args()

    if args.command == "detect":
        sys.exit(run_detection(
            args.folder_path,
            args.verbose,
            args.workers,
            args.coarse_interval,
            args.fine_interval,
            args.no_adaptive
        ))
    elif args.command == "list":
        list_pending(args.status)
    elif args.command == "clear-import":
        sys.exit(clear_import(args.confirm))
    elif args.command == "split":
        sys.exit(run_split(
            args.input_path,
            args.timestamps,
            args.output_dir,
            args.verbose
        ))
    elif args.command == "slowmo":
        sys.exit(run_slowmo(
            args.input_path,
            args.speed,
            args.output_dir,
            args.verbose
        ))
    elif args.command == "transition":
        sys.exit(run_transition(
            args.file1_path,
            args.file2_path,
            args.transition_duration,
            args.output_dir,
            not args.no_intermediate,
            args.transition_only,
            args.verbose
        ))
    elif args.command == "animated-pax-intro":
        sys.exit(run_animated_pax_intro(
            args.name,
            args.template_id,
            args.output,
            args.duration,
            args.width,
            args.height,
            args.fps,
            args.codec,
            args.verbose
        ))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

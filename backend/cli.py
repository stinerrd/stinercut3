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
            workload = data.get('workload_uuid', 'none')
            print(f"  ✓ {filename}: {classification} ({segments} segments)")
            if workload and workload != 'none':
                print(f"    QR detected: {workload}")

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
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Video detection WebSocket command handlers.
Handles videofile:start_detection and gopro:copy_completed signals.
"""
import asyncio
from typing import Optional, Callable, Any

from database import SessionLocal
from services.video_analyzer import VideoAnalyzer


async def handle_start_detection(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle videofile:start_detection command.

    Expected data:
        folder_path: str - Relative path to folder (e.g., "input/abc123")

    Returns:
        dict with status and batch_id or error
    """
    folder_path = data.get("folder_path")

    if not folder_path:
        return {
            "success": False,
            "error": "Missing folder_path in request"
        }

    # Create async progress callback that broadcasts to frontend
    async def progress_callback(event_type: str, event_data: dict):
        message = {
            "command": f"videofile:{event_type}",
            "sender": "backend",
            "target": "frontend",
            "data": event_data
        }
        await broadcast_callback(message)

    # Run analysis in background task
    asyncio.create_task(_run_analysis(folder_path, progress_callback))

    return {
        "success": True,
        "message": f"Analysis started for {folder_path}"
    }


async def handle_gopro_copy_completed(
    data: dict,
    broadcast_callback: Callable[[dict], Any]
) -> dict:
    """
    Handle gopro:copy_completed command (auto-trigger from detector).

    Expected data:
        folder_path: str - Relative path to copied folder
        source: str - Source identifier (e.g., "GOPRO")

    Returns:
        dict with status
    """
    folder_path = data.get("folder_path")

    if not folder_path:
        return {
            "success": False,
            "error": "Missing folder_path in request"
        }

    # Create async progress callback
    async def progress_callback(event_type: str, event_data: dict):
        message = {
            "command": f"videofile:{event_type}",
            "sender": "backend",
            "target": "frontend",
            "data": event_data
        }
        await broadcast_callback(message)

    # Run analysis in background task
    asyncio.create_task(_run_analysis(folder_path, progress_callback))

    return {
        "success": True,
        "message": f"Auto-analysis triggered for {folder_path}"
    }


async def _run_analysis(
    folder_path: str,
    progress_callback: Callable[[str, dict], Any]
):
    """
    Run video analysis in background.

    Args:
        folder_path: Relative path to folder
        progress_callback: Async callback for progress updates
    """
    db = SessionLocal()
    try:
        analyzer = VideoAnalyzer(db)
        batch = await analyzer.analyze_folder(folder_path, progress_callback)

        # Send final completion message
        await progress_callback("analysis_completed", {
            "batch_id": batch.uuid,
            "status": batch.status,
            "resolution_type": batch.resolution_type,
            "total_files": batch.total_files,
            "analyzed_files": batch.analyzed_files,
            "detected_qr_count": batch.detected_qr_count,
            "detected_freefall_count": batch.detected_freefall_count,
            "error_message": batch.error_message
        })

    except Exception as e:
        print(f"[VideoAnalysis] Error analyzing {folder_path}: {e}")
        await progress_callback("analysis_error", {
            "folder_path": folder_path,
            "error": str(e)
        })
    finally:
        db.close()

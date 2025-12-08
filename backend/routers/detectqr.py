"""
QR Code Detection Router
Extracts frames from video files and detects QR codes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from PIL import Image
from pyzbar.pyzbar import decode
import io
import os
import asyncio

from services.ffmpeg_service import FFmpegService

router = APIRouter(prefix="/api/detectqr", tags=["detectqr"])

VIDEODATA_PATH = os.getenv("VIDEODATA_PATH", "/videodata")

ffmpeg_service = FFmpegService()


class DetectQRRequest(BaseModel):
    video_path: str


class DetectQRResponse(BaseModel):
    success: bool
    qr_content: str | None = None
    frame_timestamp: float | None = None
    attempts: int
    message: str | None = None


def detect_qr_in_image(image_bytes: bytes) -> str | None:
    """Detect QR code in image bytes, return content or None."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        decoded = decode(image)
        if decoded:
            return decoded[0].data.decode('utf-8')
        return None
    except Exception:
        return None


def calculate_timestamps(duration: float) -> list[float]:
    """Calculate timestamps to try for QR detection."""
    # Fixed timestamps for early video
    timestamps = [0.0, 1.0, 2.0, 5.0]

    # Percentage-based timestamps for longer videos
    if duration > 10:
        timestamps.extend([
            duration * 0.10,
            duration * 0.25,
            duration * 0.50,
            duration * 0.75,
        ])

    # Filter out timestamps beyond video duration and remove duplicates
    timestamps = sorted(set(t for t in timestamps if t < duration))

    return timestamps[:8]  # Max 8 attempts


def scan_video_for_qr(video_path: str) -> dict:
    """
    Scan video for QR code by extracting frames at multiple timestamps.
    Returns result dict with success, qr_content, frame_timestamp, attempts.
    """
    # Get video duration
    try:
        duration = ffmpeg_service.get_duration(video_path)
    except ValueError as e:
        raise ValueError(f"Cannot read video: {str(e)}")

    timestamps = calculate_timestamps(duration)

    for attempt, timestamp in enumerate(timestamps, 1):
        try:
            # Extract frame
            frame_bytes = ffmpeg_service.extract_frame(video_path, timestamp)

            # Try to detect QR code
            qr_content = detect_qr_in_image(frame_bytes)

            if qr_content:
                return {
                    "success": True,
                    "qr_content": qr_content,
                    "frame_timestamp": timestamp,
                    "attempts": attempt,
                    "message": None
                }
        except ValueError:
            # Frame extraction failed, try next timestamp
            continue

    return {
        "success": False,
        "qr_content": None,
        "frame_timestamp": None,
        "attempts": len(timestamps),
        "message": f"No QR code detected after scanning {len(timestamps)} frames"
    }


@router.post("", response_model=DetectQRResponse)
async def detect_qr(request: DetectQRRequest):
    """
    Detect QR code in a video file.

    Extracts frames at multiple timestamps and scans for QR codes.
    Returns the first QR code found or a not-found response.
    """
    # Security: prevent path traversal
    if ".." in request.video_path:
        raise HTTPException(
            status_code=400,
            detail="Invalid video path: path traversal not allowed"
        )

    # Build absolute path
    video_path = os.path.join(VIDEODATA_PATH, request.video_path)

    # Check file exists
    if not os.path.isfile(video_path):
        raise HTTPException(
            status_code=404,
            detail=f"Video file not found: {request.video_path}"
        )

    # Run QR detection in thread pool (blocking FFmpeg operations)
    try:
        result = await asyncio.to_thread(scan_video_for_qr, video_path)
        return DetectQRResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )

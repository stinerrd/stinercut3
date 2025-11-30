"""Service control router for managing host services.

Note: Most detector control (status, enable, disable) is now handled via WebSocket
through the unified hub. Only restart remains here for debugging purposes.
"""

import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/services", tags=["services"])

# Detector control URL - configurable via environment
DETECTOR_URL = os.getenv("DETECTOR_URL", "http://host.docker.internal:8001")


@router.post("/detector/restart")
async def restart_detector():
    """
    Restart the detector service.

    Sends a restart command to the detector's HTTP control API.
    The service will shut down cleanly and systemd will restart it.

    Note: This endpoint uses HTTP directly to the detector's control API
    because restart is a management operation, not a real-time control command.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DETECTOR_URL}/control/restart",
                timeout=5.0,
            )
            response.raise_for_status()
            return {
                "status": "restarting",
                "message": "Detector service restart requested",
            }
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to detector service - may be stopped",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Detector service timeout",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Detector service error: {e.response.status_code}",
        )

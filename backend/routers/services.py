"""Service control router for managing host services."""

import os

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/services", tags=["services"])

# Detector control URL - configurable via environment
DETECTOR_URL = os.getenv("DETECTOR_URL", "http://host.docker.internal:8001")


@router.get("/detector/status")
async def get_detector_status():
    """
    Get detector service status.

    Returns the current state of the detector service including
    whether it's running and the number of pending device events.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DETECTOR_URL}/status", timeout=5.0)
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        return {
            "running": False,
            "error": "Cannot connect to detector service",
            "service": "stinercut-detector",
        }
    except httpx.TimeoutException:
        return {
            "running": False,
            "error": "Detector service timeout",
            "service": "stinercut-detector",
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Detector service error: {e.response.status_code}",
        )


@router.post("/detector/enable")
async def enable_detector():
    """
    Enable detector monitoring.

    Sends an enable command to the detector's HTTP control API
    to start processing device events.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DETECTOR_URL}/control/enable",
                timeout=5.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to detector service",
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


@router.post("/detector/disable")
async def disable_detector():
    """
    Disable detector monitoring.

    Sends a disable command to the detector's HTTP control API
    to stop processing device events. The daemon continues running.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{DETECTOR_URL}/control/disable",
                timeout=5.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to detector service",
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


@router.post("/detector/restart")
async def restart_detector():
    """
    Restart the detector service.

    Sends a restart command to the detector's HTTP control API.
    The service will shut down cleanly and systemd will restart it.
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

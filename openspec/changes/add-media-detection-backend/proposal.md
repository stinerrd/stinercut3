# Change: Add Media Detection Backend API

## Why
When the host service detects removable media, the backend needs to analyze the content to determine if it contains GoPro media. The backend should scan the mount point for GoPro folder structures, classify the media type, count files, and provide this information to the frontend via API and WebSocket.

## What Changes
- Create device API endpoints for mount/unmount notifications
- Implement GoPro folder detection (DCIM/[0-9]*GOPRO pattern)
- Implement media classification (video/photo/multi/empty)
- Implement media file counting (.MP4, .JPG)
- Store connected devices in memory
- Broadcast device events via WebSocket to frontend

## Impact
- Affected specs: `media-detection-backend` (new capability)
- Affected code:
  - `backend/routers/devices.py` - Device API endpoints
  - `backend/services/media_scanner.py` - GoPro detection logic
  - `backend/main.py` - Router registration, WebSocket setup

## Dependencies
- Requires: `add-media-detection-host` (sends mount events)
- Required by: `add-media-detection-frontend` (displays devices)

## Note
Backend accesses mount points via shared volume. The host service mount path must be accessible to the Docker container (e.g., bind mount /media to container).

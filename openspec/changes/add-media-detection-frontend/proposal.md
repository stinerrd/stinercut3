# Change: Add Media Detection Frontend UI

## Why
Users need to see which GoPro media devices are connected and be able to initiate imports. The frontend should display connected devices with their media information and provide import actions.

## What Changes
- Create device list UI component showing connected devices
- Display device details: mount path, media type, video/photo counts
- Add "Import" button for each device to initiate import workflow
- Connect to WebSocket for real-time device updates
- Auto-update UI when devices are added or removed

## Impact
- Affected specs: `media-detection-frontend` (new capability)
- Affected code:
  - `frontend/templates/` - Device list template
  - `frontend/src/Controller/` - Device controller (if needed)
  - `frontend/assets/` - JavaScript for WebSocket connection

## Dependencies
- Requires: `add-media-detection-backend` (provides API and WebSocket)

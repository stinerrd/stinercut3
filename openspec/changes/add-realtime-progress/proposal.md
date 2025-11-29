# Change: Add Real-time Progress Updates

## Why
Users need to see live progress during video rendering. The original stinercut uses an observer pattern for progress callbacks. The web version needs WebSocket-based real-time updates to show processing steps and percentage completion.

## What Changes
- Implement WebSocket endpoint for job progress streaming
- Create observer pattern for VideoProcessor to emit progress events
- Implement frontend WebSocket client to receive updates
- Create progress bar UI component
- Add real-time log/status message display

## Impact
- Affected specs: `realtime-updates` (new capability)
- Affected code:
  - `backend/routers/websocket.py` - WebSocket endpoint
  - `backend/services/video_processor.py` - Add observer callbacks
  - `frontend/assets/js/job-progress.js` - WebSocket client
  - `frontend/templates/project/show.html.twig` - Progress UI

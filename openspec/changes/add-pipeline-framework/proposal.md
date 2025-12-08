# Change: Add Video Processing Pipeline Framework

## Why

The backend needs a flexible, event-driven pipeline system for video processing triggered by SD card detection. The system must support:
- Parallel step execution with dependency resolution
- Dynamic step spawning during execution (e.g., spawn metadata extraction as each file is copied)
- Retry capability from failed steps without restarting entire pipeline
- Multi-worker support via Redis queue for CPU-intensive FFmpeg operations
- **Smart incremental import**: Only copy NEW videos from SD card (TM may do 10+ jumps/day)
- **QR code recognition**: Small video before each jump contains QR with passenger/booking info
- **Cross-platform**: Works on Linux and Windows (Detector copies files to shared volume)

## Workflow

1. **SD card inserted** → Detector scans file list (metadata only, not content)
2. **Detector sends file list** via WebSocket to backend (filename, size, date)
3. **Backend checks database** → identifies which files are already imported
4. **Backend requests copy of NEW small files** → Detector copies QR videos first
5. **Backend decodes QR** → extracts passenger name, booking ID from video frame
6. **Backend requests copy of remaining NEW videos** for this jump session
7. **Pipeline processes videos** → apply intro, watermark, render final output

## What Changes

- **New database tables**: `pipeline_execution`, `pipeline_step`, `pipeline_step_log`, `imported_file` (tracking)
- **New backend package**: `backend/pipeline/` with orchestrator, scheduler, worker, and step classes
- **QR decoding**: FFmpeg frame extraction + pyzbar/opencv QR recognition
- **Infrastructure**: Add Redis service to docker-compose
- **WebSocket integration**: Bidirectional communication with Detector for selective file copy
- **API endpoints**: Pipeline status, retry, and monitoring

## Impact

- Affected specs: `database` (new tables), `websocket-hub` (new message types)
- Affected code:
  - `backend/models/` - New SQLAlchemy models
  - `backend/routers/` - New pipeline router
  - `backend/routers/websocket.py` - Detector message handler
  - `docker-compose.yml` - Redis service
  - `frontend/migrations/` - New migration file
  - `backend/requirements.txt` - Add pyzbar, opencv-python-headless

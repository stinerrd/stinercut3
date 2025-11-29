## 1. Backend WebSocket
- [ ] 1.1 Create `backend/routers/websocket.py`
- [ ] 1.2 Implement WebSocket endpoint: WS /api/ws/jobs/{job_id}
- [ ] 1.3 Implement connection management (track active connections)
- [ ] 1.4 Implement broadcast function for progress updates

## 2. Observer Pattern
- [ ] 2.1 Create progress observer interface/protocol
- [ ] 2.2 Update VideoProcessor to accept observer
- [ ] 2.3 Emit progress events at each processing step
- [ ] 2.4 Emit percentage updates during FFmpeg processing
- [ ] 2.5 Parse FFmpeg progress output for accurate percentage

## 3. Progress Events
- [ ] 3.1 Define event schema: {type, step, progress, message, timestamp}
- [ ] 3.2 Implement step events: "reading_videos", "detecting_freefall", "processing_audio", etc.
- [ ] 3.3 Implement progress events: {progress: 0-100}
- [ ] 3.4 Implement completion event: {type: "completed", output_path}
- [ ] 3.5 Implement error event: {type: "error", message}

## 4. Frontend WebSocket Client
- [ ] 4.1 Create `frontend/assets/js/job-progress.js`
- [ ] 4.2 Implement WebSocket connection to backend
- [ ] 4.3 Handle connection open/close/error events
- [ ] 4.4 Parse incoming progress messages
- [ ] 4.5 Implement reconnection logic

## 5. Frontend UI
- [ ] 5.1 Create progress bar component
- [ ] 5.2 Display current step name
- [ ] 5.3 Display percentage with animation
- [ ] 5.4 Display status messages/log
- [ ] 5.5 Auto-update UI on job completion
- [ ] 5.6 Show download button when complete

## 6. Verification
- [ ] 6.1 Test WebSocket connection establishment
- [ ] 6.2 Test progress updates during render
- [ ] 6.3 Test UI updates in real-time
- [ ] 6.4 Test reconnection after disconnect
- [ ] 6.5 Test completion notification

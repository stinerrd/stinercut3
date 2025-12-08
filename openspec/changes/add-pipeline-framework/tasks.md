# Tasks: Add Pipeline Framework

## 1. Infrastructure Setup
- [ ] 1.1 Add Redis service to docker-compose.yml
- [ ] 1.2 Add `redis` and `aioredis` to backend/requirements.txt
- [ ] 1.3 Add `pyzbar` and `opencv-python-headless` to backend/requirements.txt
- [ ] 1.4 Create Redis connection utility in backend

## 2. Database Schema
- [ ] 2.1 Create migration for `pipeline_execution` table
- [ ] 2.2 Create migration for `pipeline_step` table
- [ ] 2.3 Create migration for `pipeline_step_log` table
- [ ] 2.4 Create migration for `imported_file` table (track already-imported files)
- [ ] 2.5 Run migrations and verify schema

## 3. SQLAlchemy Models
- [ ] 3.1 Create `backend/models/pipeline_execution.py`
- [ ] 3.2 Create `backend/models/pipeline_step.py`
- [ ] 3.3 Create `backend/models/pipeline_step_log.py`
- [ ] 3.4 Create `backend/models/imported_file.py`
- [ ] 3.5 Export models in `backend/models/__init__.py`

## 4. Pipeline Core Framework
- [ ] 4.1 Create `backend/pipeline/__init__.py` with package exports
- [ ] 4.2 Create `backend/pipeline/base.py` with BaseStep, StepResult, NewStep
- [ ] 4.3 Create `backend/pipeline/registry.py` with step class registration
- [ ] 4.4 Create `backend/pipeline/scheduler.py` with dependency resolution
- [ ] 4.5 Create `backend/pipeline/worker.py` with Redis consumer loop
- [ ] 4.6 Create `backend/pipeline/orchestrator.py` for detector signal handling

## 5. WebSocket Bidirectional Communication
- [ ] 5.1 Add handler for `sd:file_list` message from Detector
- [ ] 5.2 Implement `sd:copy_request` message to Detector
- [ ] 5.3 Add handler for `sd:file_copied` message from Detector
- [ ] 5.4 Add handler for `sd:copy_error` message from Detector

## 6. Incremental Import Logic
- [ ] 6.1 Create `check_imported_files` step - filter against `imported_file` table
- [ ] 6.2 Implement file identification (filename + size + modified_date hash)
- [ ] 6.3 Create `request_small_files` step - request files < 50MB first
- [ ] 6.4 Create `mark_file_imported` utility - record imported files in DB

## 7. QR Code Recognition
- [ ] 7.1 Create `backend/pipeline/qr_decoder.py` utility
- [ ] 7.2 Implement FFmpeg frame extraction (first 5 seconds, every 0.5s)
- [ ] 7.3 Implement pyzbar QR decoding from frames
- [ ] 7.4 Define QR data format (JSON with passenger_name, booking_id, etc.)
- [ ] 7.5 Create `decode_qr` pipeline step

## 8. Pipeline Steps
- [ ] 8.1 Create `backend/pipeline/steps/__init__.py`
- [ ] 8.2 Create `receive_file_list` step - handle Detector file list
- [ ] 8.3 Create `filter_new_files` step - check imported_file table
- [ ] 8.4 Create `request_qr_videos` step - request small files from Detector
- [ ] 8.5 Create `decode_qr` step - extract QR data from video
- [ ] 8.6 Create `request_session_videos` step - request remaining videos for this jump
- [ ] 8.7 Create `extract_metadata` step - FFprobe metadata extraction
- [ ] 8.8 Create `cleanup` step - remove temp files
- [ ] 8.9 Create `render_final` step - placeholder for FFmpeg render

## 9. API Integration
- [ ] 9.1 Create `backend/routers/pipeline.py` with status/retry endpoints
- [ ] 9.2 Register pipeline router in `backend/main.py`
- [ ] 9.3 Update WebSocket router for new message types

## 10. WebSocket Events to Frontend
- [ ] 10.1 Add `pipeline:started` broadcast when pipeline begins
- [ ] 10.2 Add `pipeline:step_completed` broadcast for step progress
- [ ] 10.3 Add `pipeline:qr_decoded` broadcast with passenger info
- [ ] 10.4 Add `pipeline:completed` broadcast when pipeline finishes
- [ ] 10.5 Add `pipeline:failed` broadcast on pipeline failure

## 11. Worker Management
- [ ] 11.1 Create worker entrypoint script
- [ ] 11.2 Add worker service to docker-compose.yml (or document manual start)
- [ ] 11.3 Add worker_id generation for tracking

## 12. Testing & Validation
- [ ] 12.1 Test file list receiving and filtering
- [ ] 12.2 Test incremental import (only new files copied)
- [ ] 12.3 Test QR decoding from sample video
- [ ] 12.4 Test step dependency resolution and parallel execution
- [ ] 12.5 Test retry from failed step
- [ ] 12.6 Test WebSocket progress broadcasts

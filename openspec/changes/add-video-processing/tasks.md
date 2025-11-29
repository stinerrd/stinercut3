## 1. Backend Services
- [ ] 1.1 Create `backend/services/ffmpeg_helper.py` - FFmpeg command wrapper
- [ ] 1.2 Create `backend/services/video_processor.py` - Main orchestrator
- [ ] 1.3 Implement `initial_read_videos()` - Validate and catalog videos
- [ ] 1.4 Implement `set_project_dimensions()` - Determine output resolution/codec
- [ ] 1.5 Implement `concatenate()` - Join videos using concat demuxer
- [ ] 1.6 Implement `execute()` - Run FFmpeg commands with error handling

## 2. Backend API - Jobs
- [ ] 2.1 Create `backend/routers/jobs.py`
- [ ] 2.2 Implement POST /api/projects/{id}/render - Start render job
- [ ] 2.3 Implement GET /api/jobs/{id} - Get job status
- [ ] 2.4 Implement GET /api/projects/{id}/output - Download rendered video
- [ ] 2.5 Create `backend/schemas/job.py` - Pydantic schemas

## 3. Job Management
- [ ] 3.1 Implement job queue (prevent concurrent renders overload)
- [ ] 3.2 Implement job status updates during processing
- [ ] 3.3 Implement temporary file management
- [ ] 3.4 Implement cleanup after job completion

## 4. Frontend
- [ ] 4.1 Add "Render" button to project detail page
- [ ] 4.2 Display job status (pending/processing/completed/failed)
- [ ] 4.3 Show progress percentage
- [ ] 4.4 Add download link for completed videos
- [ ] 4.5 Display error message on failure

## 5. Verification
- [ ] 5.1 Test concatenation of 2 videos same codec
- [ ] 5.2 Test concatenation of 5+ videos
- [ ] 5.3 Test job status transitions
- [ ] 5.4 Test download of completed video
- [ ] 5.5 Test error handling for invalid inputs

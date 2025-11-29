# Change: Add Video Processing Pipeline

## Why
Users need to concatenate their video clips into a single output file. This is the core rendering functionality that joins multiple videos in sequence using FFmpeg.

## What Changes
- Implement VideoProcessor service to orchestrate rendering pipeline
- Implement FFmpeg concatenation without re-encoding (when codecs match)
- Create job management system for tracking render progress
- Implement render API endpoint
- Add download endpoint for completed renders
- Create frontend render button and job status display

## Impact
- Affected specs: `video-processing` (new capability)
- Affected code:
  - `backend/services/video_processor.py` - Main processing orchestrator
  - `backend/services/ffmpeg_helper.py` - FFmpeg command wrapper
  - `backend/routers/jobs.py` - Job API endpoints
  - `frontend/templates/project/show.html.twig` - Render button, status

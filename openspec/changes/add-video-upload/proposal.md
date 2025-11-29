# Change: Add Video Upload and Management

## Why
Users need to upload videos to projects, view video metadata, reorder clips, and manage their video collections before rendering. This is the core workflow entry point.

## What Changes
- Implement video upload API endpoint with multi-file support
- Extract video metadata using ffprobe (duration, resolution, codec, FPS)
- Generate video thumbnails for preview
- Implement project CRUD operations
- Create frontend UI for project management and video upload
- Implement drag-drop video reordering

## Impact
- Affected specs: `video-management` (new capability)
- Affected code:
  - `backend/routers/projects.py` - Project API endpoints
  - `backend/routers/videos.py` - Video API endpoints
  - `backend/services/video_metadata.py` - FFprobe wrapper
  - `backend/services/file_storage.py` - Upload handling
  - `frontend/src/Controller/ProjectController.php`
  - `frontend/src/Controller/VideoController.php`
  - `frontend/templates/project/` - Project views

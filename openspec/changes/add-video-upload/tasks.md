## 1. Backend API - Projects
- [ ] 1.1 Create `backend/routers/projects.py`
- [ ] 1.2 Implement POST /api/projects - Create project
- [ ] 1.3 Implement GET /api/projects - List all projects
- [ ] 1.4 Implement GET /api/projects/{id} - Get project details
- [ ] 1.5 Implement PUT /api/projects/{id} - Update project
- [ ] 1.6 Implement DELETE /api/projects/{id} - Delete project
- [ ] 1.7 Create `backend/schemas/project.py` - Pydantic schemas

## 2. Backend API - Videos
- [ ] 2.1 Create `backend/routers/videos.py`
- [ ] 2.2 Implement POST /api/projects/{id}/videos - Upload videos
- [ ] 2.3 Implement GET /api/projects/{id}/videos - List project videos
- [ ] 2.4 Implement DELETE /api/videos/{id} - Remove video
- [ ] 2.5 Implement PUT /api/projects/{id}/videos/order - Reorder videos
- [ ] 2.6 Create `backend/schemas/video.py` - Pydantic schemas

## 3. Backend Services
- [ ] 3.1 Create `backend/services/video_metadata.py` - FFprobe extraction
- [ ] 3.2 Create `backend/services/file_storage.py` - File upload handling
- [ ] 3.3 Implement thumbnail generation using FFmpeg

## 4. Frontend - Symfony Setup
- [ ] 4.1 Install Twig: `composer require twig`
- [ ] 4.2 Create `frontend/src/Service/BackendApiClient.php`

## 5. Frontend - Project Pages
- [ ] 5.1 Create `frontend/src/Controller/ProjectController.php`
- [ ] 5.2 Create `frontend/templates/project/index.html.twig` - Project list
- [ ] 5.3 Create `frontend/templates/project/new.html.twig` - Create form
- [ ] 5.4 Create `frontend/templates/project/show.html.twig` - Project detail

## 6. Frontend - Video Management
- [ ] 6.1 Create `frontend/src/Controller/VideoController.php`
- [ ] 6.2 Implement multi-file upload form
- [ ] 6.3 Create video list component with thumbnails
- [ ] 6.4 Implement drag-drop reordering (JavaScript)

## 7. Verification
- [ ] 7.1 Test video upload end-to-end
- [ ] 7.2 Verify metadata extraction accuracy
- [ ] 7.3 Test project CRUD operations
- [ ] 7.4 Test video reordering

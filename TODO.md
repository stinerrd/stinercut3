# Tandem Video Editing Software - Implementation TODO

## Getting Started
```bash
# Build and start all containers
docker-compose up --build

# Frontend will be available at: http://localhost:8080
# Backend API will be available at: http://localhost:8000
```

## Phase 2: Frontend (Symfony) Setup

### 2.1 Initialize Symfony Project
- [ ] Enter frontend container: `docker-compose exec frontend bash`
- [ ] Create new Symfony project: `symfony new . --webapp --version=7.0`
- [ ] Install required bundles:
  - [ ] `composer require symfony/orm-pack`
  - [ ] `composer require symfony/maker-bundle --dev`
  - [ ] `composer require symfony/webpack-encore-bundle`
  - [ ] `composer require symfony/mercure-bundle` (for WebSocket)
  - [ ] `composer require symfony/http-client`

### 2.2 Frontend Application Structure
- [ ] Create controllers:
  - [ ] `VideoController` - Handle video upload, list, delete
  - [ ] `EditorController` - Serve video editor interface
  - [ ] `ProjectController` - Manage editing projects
  - [ ] `JobController` - Monitor processing jobs
- [ ] Create entities:
  - [ ] `Session` - Session management
  - [ ] `Project` - Video editing projects
  - [ ] `EditOperation` - Individual edit operations
  - [ ] `Job` - Processing job tracking
  - [ ] `Video` - Video file metadata
- [ ] Create services:
  - [ ] `BackendApiClient` - Communicate with Python backend
  - [ ] `VideoService` - Video management logic
  - [ ] `SessionService` - Session handling

### 2.3 Frontend UI Development
- [ ] Set up Webpack Encore for asset compilation
- [ ] Install Node.js dependencies:
  - [ ] `npm install video.js`
  - [ ] `npm install axios` (for API calls)
  - [ ] `npm install @hotwired/stimulus` (already included in webapp)
- [ ] Create video editor interface:
  - [ ] Video upload form with drag-and-drop
  - [ ] Video player with Video.js
  - [ ] Timeline/scrubber interface
  - [ ] Effects panel (filters, transitions)
  - [ ] Text overlay tool
  - [ ] Audio controls
- [ ] Create WebSocket client for real-time updates
- [ ] Add progress indicators for video processing

### 2.4 Frontend Routing
- [ ] `/` - Home/video list page
- [ ] `/upload` - Video upload page
- [ ] `/editor/{projectId}` - Video editor interface
- [ ] `/jobs` - Job status page
- [ ] `/api/*` - REST API endpoints for frontend-backend communication

## Phase 3: Backend (Python + FFmpeg) Setup

### 3.1 Initialize Python Application
- [ ] Create `main.py` with FastAPI app initialization
- [ ] Set up database connection with SQLAlchemy
- [ ] Configure CORS for frontend communication
- [ ] Set up WebSocket endpoint

### 3.2 Backend Application Structure
```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Already created
├── config.py              # Configuration management
├── database.py            # Database connection
├── models/                # SQLAlchemy models
│   ├── __init__.py
│   ├── session.py
│   ├── project.py
│   ├── edit_operation.py
│   ├── job.py
│   └── video.py
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── videos.py          # Video upload/management
│   ├── projects.py        # Project management
│   ├── jobs.py            # Job status
│   └── websocket.py       # WebSocket connections
├── services/              # Business logic
│   ├── __init__.py
│   ├── video_processor.py # FFmpeg operations
│   ├── job_manager.py     # Job queue management
│   └── effects.py         # Video effects library
└── utils/                 # Utility functions
    ├── __init__.py
    └── ffmpeg_helper.py   # FFmpeg wrapper utilities
```

### 3.3 Backend API Endpoints
- [ ] `POST /api/videos/upload` - Upload video file
- [ ] `GET /api/videos` - List all videos
- [ ] `DELETE /api/videos/{id}` - Delete video
- [ ] `POST /api/projects` - Create new project
- [ ] `GET /api/projects/{id}` - Get project details
- [ ] `POST /api/projects/{id}/operations` - Add edit operation
- [ ] `POST /api/projects/{id}/render` - Start rendering
- [ ] `GET /api/jobs/{id}` - Get job status
- [ ] `WS /ws/{jobId}` - WebSocket for real-time updates

### 3.4 Video Processing Features
- [ ] **Basic Operations**:
  - [ ] Trim video (start/end times)
  - [ ] Cut video (remove middle section)
  - [ ] Concatenate multiple clips
  - [ ] Extract thumbnail at specific timestamp
- [ ] **Filters & Effects**:
  - [ ] Brightness adjustment
  - [ ] Contrast adjustment
  - [ ] Saturation adjustment
  - [ ] Blur effect
  - [ ] Sharpen effect
  - [ ] Grayscale/Sepia filters
- [ ] **Transitions**:
  - [ ] Fade in/out
  - [ ] Crossfade between clips
  - [ ] Wipe transitions
- [ ] **Text Overlay**:
  - [ ] Add text at specific position
  - [ ] Font, size, color customization
  - [ ] Duration control
- [ ] **Audio**:
  - [ ] Volume adjustment
  - [ ] Fade in/out
  - [ ] Mix multiple audio tracks
  - [ ] Extract/replace audio

### 3.5 FFmpeg Integration
Create helper functions in `services/video_processor.py`:
```python
# Example structure (to be implemented)
class VideoProcessor:
    async def trim_video(input_path, output_path, start, end)
    async def apply_filter(input_path, output_path, filter_name, params)
    async def add_text_overlay(input_path, output_path, text, position, style)
    async def concatenate_videos(input_paths, output_path)
    async def add_transition(clip1, clip2, output_path, transition_type)
    async def adjust_audio(input_path, output_path, volume)
    async def generate_thumbnail(video_path, output_path, timestamp)
```

### 3.6 WebSocket Implementation
- [ ] Set up WebSocket manager for connection handling
- [ ] Implement progress callback from FFmpeg
- [ ] Send real-time updates: `{"status": "processing", "progress": 45, "message": "Applying filters..."}`
- [ ] Handle client disconnections gracefully

## Phase 4: Database Setup

### 4.1 Create Database Schema
- [ ] Run migrations to create tables:
  - [ ] `sessions` table
  - [ ] `projects` table
  - [ ] `edit_operations` table
  - [ ] `jobs` table
  - [ ] `videos` table

### 4.2 Database Models (both Symfony and Python)
Tables needed:
```sql
-- sessions
CREATE TABLE sessions (
    id VARCHAR(128) PRIMARY KEY,
    data TEXT,
    time INT,
    lifetime INT
);

-- videos
CREATE TABLE videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    path VARCHAR(512),
    duration FLOAT,
    width INT,
    height INT,
    format VARCHAR(50),
    size BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- projects
CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(128),
    name VARCHAR(255),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- edit_operations
CREATE TABLE edit_operations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    operation_type VARCHAR(50), -- 'trim', 'filter', 'text', 'transition', etc.
    parameters JSON,
    operation_order INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- jobs
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    status ENUM('pending', 'processing', 'completed', 'failed'),
    progress INT DEFAULT 0,
    output_path VARCHAR(512),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
```

## Phase 5: Integration & Testing

### 5.1 Frontend-Backend Integration
- [ ] Test video upload flow
- [ ] Test project creation and operation storage
- [ ] Test render job submission
- [ ] Test WebSocket real-time updates
- [ ] Test video file serving from shared volume

### 5.2 Video Processing Pipeline Testing
- [ ] Test each FFmpeg operation individually
- [ ] Test operation chaining (multiple effects)
- [ ] Test error handling for invalid inputs
- [ ] Test progress reporting accuracy
- [ ] Test output file quality

### 5.3 Session Management Testing
- [ ] Test session creation and persistence
- [ ] Test session expiry
- [ ] Test multiple concurrent sessions

## Phase 6: Additional Features & Optimization

### 6.1 Performance
- [ ] Implement video chunking for large uploads
- [ ] Add caching for thumbnails
- [ ] Optimize FFmpeg parameters for quality/speed
- [ ] Add progress estimation for complex operations

### 6.2 User Experience
- [ ] Add preview generation after each operation
- [ ] Implement undo/redo functionality
- [ ] Add keyboard shortcuts in editor
- [ ] Add drag-and-drop timeline reordering
- [ ] Add export quality options

### 6.3 Error Handling
- [ ] Add validation for video formats
- [ ] Handle disk space issues
- [ ] Handle FFmpeg errors gracefully
- [ ] Add user-friendly error messages

### 6.4 Documentation
- [ ] Create API documentation (Swagger/OpenAPI)
- [ ] Document FFmpeg parameters used
- [ ] Create user guide for video editor
- [ ] Add code comments for complex operations

## Development Workflow

### Starting Development
```bash
# Start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

### Frontend Development
```bash
# Enter frontend container
docker-compose exec frontend bash

# Install PHP dependencies
composer install

# Run database migrations
php bin/console doctrine:migrations:migrate

# Install Node.js dependencies
npm install

# Build assets
npm run dev

# Watch for changes
npm run watch
```

### Backend Development
```bash
# Enter backend container
docker-compose exec backend bash

# Install Python dependencies (already in Dockerfile)
pip install -r requirements.txt

# Run with auto-reload (already in CMD)
uvicorn main:app --reload
```

### Database Access
```bash
# Access MySQL
docker-compose exec mysql mysql -u tandem_user -ptandem_pass tandem_db
```

## Shared Storage Structure
```
/shared-videos/
├── uploads/          # Original uploaded videos
│   └── {video_id}/
│       └── original.mp4
├── temp/             # Temporary processing files
│   └── {job_id}/
│       ├── clip1.mp4
│       └── clip2.mp4
├── output/           # Final rendered videos
│   └── {job_id}/
│       └── final.mp4
└── thumbnails/       # Video thumbnails
    └── {video_id}.jpg
```

## Notes
- Session-based authentication means no user registration/login required
- WebSocket updates provide real-time progress feedback
- MySQL stores all metadata and job information
- Shared volume allows both frontend and backend to access video files
- FFmpeg runs in backend container for all processing
- Frontend serves static files and communicates with backend API

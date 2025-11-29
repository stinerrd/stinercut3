# Project Context

## Purpose
Tandem Video Editing Software - A web-based video editing application with session-based workflow. Users can upload videos, apply edits (trim, filters, transitions, text overlays, audio adjustments), and render final output with real-time progress updates via WebSocket. No user registration required; projects are associated with browser sessions.

## Tech Stack

### Frontend
- **Symfony 7** (PHP 8.3-fpm + Nginx) - Web application framework
- **Doctrine ORM** - Database abstraction layer
- **Webpack Encore** - Asset management (JS/CSS bundling)
- **Video.js** - HTML5 video player library
- **Mercure** - WebSocket/SSE for real-time updates
- **Stimulus** - JavaScript framework (Symfony Hotwire)

### Backend
- **Python 3.11** + **FastAPI** - Video processing API
- **FFmpeg** + **ffmpeg-python** - Video processing engine
- **SQLAlchemy** - Python ORM for database operations
- **Uvicorn** - ASGI server

### Infrastructure
- **Docker Compose** - Container orchestration
- **MySQL 8.0** - Database for sessions, projects, jobs, metadata
- **Shared Docker volume** (`/shared-videos/`) - Video file storage accessible by both services

## Project Conventions

### Code Style

#### PHP (Frontend)
- Follow Symfony coding standards
- Use Doctrine entities for database models
- Services for business logic (BackendApiClient, VideoService, SessionService)
- Twig templates for views

#### Python (Backend)
- FastAPI router pattern for API endpoints
- SQLAlchemy models in `models/` directory
- Business logic in `services/` (video_processor, job_manager, effects)
- Utility functions in `utils/` (ffmpeg_helper)

#### File Naming
- PHP: PascalCase for classes, camelCase for methods/variables
- Python: snake_case for files, functions, variables; PascalCase for classes

### Architecture Patterns

#### Service Communication
- Frontend (port 8080) → Backend (port 8000) via REST API
- Backend → Frontend via WebSocket for real-time progress updates
- Both services → MySQL (port 3306) for data persistence
- Both services → `/shared-videos/` volume for video file access

#### Directory Structure
```
frontend/           # Symfony application
├── src/
│   ├── Controller/ # HTTP request handlers
│   ├── Entity/     # Doctrine ORM models
│   └── Service/    # Business logic
├── templates/      # Twig templates
└── assets/         # JS/CSS (Webpack Encore)

backend/            # FastAPI application
├── main.py         # Entry point
├── routers/        # API endpoints
├── services/       # Business logic
├── models/         # SQLAlchemy models
└── utils/          # Helper functions
```

#### Shared Storage Structure
```
/shared-videos/
├── uploads/      # Original uploaded videos
├── temp/         # Temporary processing files
├── output/       # Final rendered videos
└── thumbnails/   # Video preview thumbnails
```

### Testing Strategy
- Test video upload flow end-to-end
- Test each FFmpeg operation individually
- Test WebSocket real-time updates
- Test session creation, persistence, and expiry
- Test error handling for invalid inputs

### Git Workflow
- Main branch: `main`
- Feature branches for new work
- OpenSpec proposals for architectural changes

## Domain Context

### Video Editing Operations
- **Basic**: Trim, cut, concatenate clips
- **Filters**: Brightness, contrast, saturation, blur, sharpen, grayscale
- **Transitions**: Fade in/out, crossfade, wipe
- **Text**: Overlay text with customizable position, font, color
- **Audio**: Volume adjustment, fade, mixing

### Data Flow
1. User uploads video via Frontend → saved to `/shared-videos/uploads/`
2. User creates project and adds operations → stored in MySQL
3. User triggers render → Frontend sends request to Backend
4. Backend creates job → processes video with FFmpeg → saves to `/shared-videos/output/`
5. Backend sends progress updates via WebSocket → Frontend displays real-time progress
6. Job completes → Frontend allows download of processed video

### Session Management
- Sessions stored in MySQL
- Projects associated with session ID
- No login/registration required
- Sessions expire after inactivity

## Important Constraints

- All video file paths in database must be relative to `/shared-videos/`
- Backend must access shared volume at `/shared-videos/`
- Frontend public directory: `/frontend/public` (Nginx serves from here)
- Database connection: `mysql://tandem_user:tandem_pass@mysql:3306/tandem_db`
- Backend API base URL from frontend: `http://backend:8000`

## External Dependencies

### Docker Services
- `frontend` - PHP 8.3-fpm + Nginx (port 8080)
- `backend` - Python 3.11 + FastAPI (port 8000)
- `mysql` - MySQL 8.0 (port 3306)

### Key Libraries
- FFmpeg (video processing)
- Video.js (HTML5 player)
- Mercure (real-time updates)

### Development Tools
- Docker Compose for local development
- Hot reload enabled for both frontend and backend
- Webpack watch mode for frontend assets

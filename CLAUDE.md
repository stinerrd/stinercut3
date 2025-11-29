<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tandem Video Editing Software** - Web-based video editing application with session-based workflow.

- **Frontend**: Symfony 7 (PHP 8.3-fpm + Nginx) - Web interface for video editing
- **Backend**: Python 3.11 + FastAPI + FFmpeg - Video processing engine
- **Database**: MySQL 8.0 - Stores sessions, projects, jobs, and metadata
- **Storage**: Shared Docker volume for video files accessible by both services

## Commands

### Docker Operations
```bash
# Start all services
docker-compose up -d

# Build and start (after Dockerfile changes)
docker-compose up --build

# View logs
docker-compose logs -f [service_name]

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Frontend (Symfony)
```bash
# Enter frontend container
docker-compose exec frontend bash

# Initialize Symfony project (first time only)
symfony new . --webapp --version=7.0

# Install PHP dependencies
composer install

# Run migrations
php bin/console doctrine:migrations:migrate

# Install Node.js dependencies
npm install

# Build assets
npm run dev

# Watch for changes during development
npm run watch

# Clear cache
php bin/console cache:clear
```

### Backend (Python)
```bash
# Enter backend container
docker-compose exec backend bash

# Install dependencies (if requirements.txt changes)
pip install -r requirements.txt

# Run manually (auto-reload enabled by default)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Database
```bash
# Access MySQL CLI
docker-compose exec mysql mysql -u tandem_user -ptandem_pass tandem_db

# Create database backup
docker-compose exec mysql mysqldump -u tandem_user -ptandem_pass tandem_db > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u tandem_user -ptandem_pass tandem_db < backup.sql
```

## Architecture

### Service Communication
- Frontend (port 8080) → Backend (port 8000) via REST API
- Frontend ← Backend via WebSocket for real-time progress updates
- Both services → MySQL (port 3306) for data persistence
- Both services → /shared-videos volume for video file access

### Shared Storage Structure
```
/shared-videos/
├── uploads/      # Original uploaded videos
├── temp/         # Temporary processing files
├── output/       # Final rendered videos
└── thumbnails/   # Video preview thumbnails
```

### Data Flow
1. User uploads video via Frontend → saved to /shared-videos/uploads/
2. User creates project and adds operations → stored in MySQL
3. User triggers render → Frontend sends request to Backend
4. Backend creates job → processes video with FFmpeg → saves to /shared-videos/output/
5. Backend sends progress updates via WebSocket → Frontend displays real-time progress
6. Job completes → Frontend allows download of processed video

### Frontend Structure (Symfony)
- Controllers: Handle HTTP requests, render views
- Entities: Doctrine ORM models (Session, Project, EditOperation, Job, Video)
- Services: Business logic (BackendApiClient, VideoService, SessionService)
- Templates: Twig templates for UI
- Assets: JavaScript/CSS managed by Webpack Encore

### Backend Structure (Python)
- main.py: FastAPI application entry point
- routers/: API endpoint handlers (videos, projects, jobs, websocket)
- services/: Business logic (video_processor, job_manager, effects)
- models/: SQLAlchemy ORM models
- utils/: Helper functions (ffmpeg_helper)

## Key Technologies

### Frontend Stack
- **Symfony 7**: PHP framework for web application
- **Doctrine ORM**: Database abstraction layer
- **Webpack Encore**: Asset management (JS/CSS bundling)
- **Video.js**: HTML5 video player library
- **Mercure**: WebSocket/SSE for real-time updates
- **Stimulus**: JavaScript framework (included in Symfony webapp)

### Backend Stack
- **FastAPI**: Modern Python web framework
- **FFmpeg**: Video processing engine
- **ffmpeg-python**: Python wrapper for FFmpeg
- **SQLAlchemy**: Python ORM for database operations
- **Uvicorn**: ASGI server for FastAPI
- **WebSockets**: Real-time bidirectional communication

## Video Processing Features

The backend implements these FFmpeg-based operations:
- **Basic**: Trim, cut, concatenate clips
- **Filters**: Brightness, contrast, saturation, blur, sharpen, grayscale
- **Transitions**: Fade in/out, crossfade, wipe
- **Text**: Overlay text with customizable position, font, color
- **Audio**: Volume adjustment, fade, mixing

## Session Management

Uses session-based authentication (no user accounts):
- Sessions stored in MySQL
- Projects associated with session ID
- No login/registration required
- Sessions expire after inactivity

## Development Workflow

1. Make changes to frontend code in `/frontend` directory
2. Make changes to backend code in `/backend` directory
3. Changes are reflected immediately due to volume mounts and hot reload
4. Frontend Webpack watch mode auto-compiles assets
5. Backend uvicorn auto-reloads on Python file changes

## IDE Support

### PyCharm Community Edition
- Use integrated terminal for all Docker commands
- Docker GUI integration requires PyCharm Professional
- Terminal access: **View** → **Tool Windows** → **Terminal**
- All commands in this file work from PyCharm's terminal

### PyCharm Professional
- Full Docker integration available in Services panel
- Configure: **Settings** → **Docker** → Add Unix socket connection
- Access: **View** → **Tool Windows** → **Services**

### VS Code
- Install "Docker" extension by Microsoft for full Docker Compose support
- View containers, logs, and manage services from sidebar

## Important Notes

- Frontend public directory: `/frontend/public` (Nginx serves from here)
- Backend must access shared volume at `/shared-videos`
- Database connection string: `mysql://tandem_user:tandem_pass@mysql:3306/tandem_db`
- Backend API base URL from frontend: `http://backend:8000`
- All video file paths in database should be relative to `/shared-videos/`

## Next Steps

See `TODO.md` for detailed implementation roadmap covering:
- Symfony project initialization and bundle installation
- Backend API endpoint implementation
- Database schema and migrations
- Video processing pipeline development
- Frontend UI/editor interface
- WebSocket real-time updates integration

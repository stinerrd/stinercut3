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

**Stinercut** - Web-based video editing application for tandem skydiving videos.

- **Frontend**: Symfony 7 (PHP 8.3-fpm + Nginx) with Eloquent ORM
- **Backend**: Python 3.11 + FastAPI + FFmpeg - Video processing engine
- **Database**: MySQL 8.0 - Stores projects, jobs, assets, and settings
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

# Install PHP dependencies
composer install

# Run migrations
php bin/console eloquent:migrate

# Rollback migrations
php bin/console eloquent:migrate:rollback

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
docker-compose exec -T mysql mysql -u stiner -plocal stinercut

# Create database backup
docker-compose exec -T mysql mysqldump -u stiner -plocal stinercut > backup.sql

# Restore database
docker-compose exec -T mysql mysql -u stiner -plocal stinercut < backup.sql
```

## Architecture

### Service Communication
- Frontend (via Traefik at stinercut.local) → Backend (api.stinercut.local) via REST API
- Frontend ← Backend via WebSocket for real-time progress updates
- Both services → MySQL (port 3306 internal, 3307 external) for data persistence
- Both services → /shared-videos volume for video file access
- Both services → /videodata bind mount for project/workload configuration data

### Shared Storage Structure
```
/shared-videos/
├── uploads/      # Original uploaded videos
├── temp/         # Temporary processing files
├── output/       # Final rendered videos
└── thumbnails/   # Video preview thumbnails
```

### Video Data Storage Structure
```
/videodata/
├── projects/     # Project-specific configuration
├── workloads/    # Workload metadata and configuration
└── cache/        # Optional: cached data files
```

### Frontend Structure (Symfony + Eloquent)
```
frontend/
├── src/
│   ├── Controller/       # HTTP request handlers
│   │   ├── HomeController.php
│   │   ├── SettingsController.php
│   │   └── VideographersController.php
│   └── Models/           # Eloquent ORM models
│       ├── Project.php
│       ├── Video.php
│       ├── Job.php
│       ├── Asset.php
│       ├── Setting.php
│       └── Videographer.php
├── templates/            # Twig templates
├── migrations/           # Eloquent migrations
└── assets/               # JS/CSS (Webpack Encore)
```

### Backend Structure (Python + FastAPI)
```
backend/
├── main.py               # FastAPI entry point
├── database.py           # SQLAlchemy connection
├── routers/
│   ├── services.py       # Service control endpoints
│   └── websocket.py      # WebSocket handler
└── models/
    ├── project.py
    ├── video.py
    ├── job.py
    ├── asset.py
    └── setting.py
```

## Key Technologies

### Frontend Stack
- **Symfony 7**: PHP framework for web application
- **Eloquent ORM**: Laravel's database abstraction (via wouterj/eloquent-bundle)
- **AdminLTE 3**: Dashboard UI theme
- **Twig**: Template engine

### Backend Stack
- **FastAPI**: Modern Python web framework
- **FFmpeg**: Video processing engine
- **SQLAlchemy**: Python ORM for database operations
- **Uvicorn**: ASGI server for FastAPI
- **WebSockets**: Real-time bidirectional communication

## Database

### Connection Details
- **Host**: localhost (external) / mysql (internal)
- **Port**: 3307 (external) / 3306 (internal)
- **Database**: stinercut
- **Username**: stiner
- **Password**: local
- **Connection string**: `mysql://stiner:local@mysql:3306/stinercut`

### Tables
- `projects` - Video editing projects
- `videos` - Video file metadata
- `jobs` - Processing job tracking
- `assets` - Intro/outro/watermark assets
- `settings` - Application settings
- `videographer` - Videographer profiles
- `migrations` - Eloquent migration tracking

## Development Workflow

1. Make changes to frontend code in `/frontend` directory
2. Make changes to backend code in `/backend` directory
3. Changes are reflected immediately due to volume mounts and hot reload
4. Backend uvicorn auto-reloads on Python file changes

## URLs

- **Frontend**: https://stinercut.local (via Traefik)
- **Backend API**: https://api.stinercut.local (via Traefik)
- **Backend direct**: http://localhost:8002

## Important Notes

- Frontend public directory: `/frontend/public` (Nginx serves from here)
- Backend must access shared volume at `/shared-videos`
- All video file paths in database should be relative to `/shared-videos/`
- Uses Eloquent ORM (not Doctrine) for frontend database operations
- create files readable for all
- `/videodata` contains project/workload configuration and metadata files
- All videodata file paths should be relative to `/videodata/`
- Frontend and backend both have read/write access to `/videodata`
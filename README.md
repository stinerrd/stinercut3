# Tandem Video Editing Software

Web-based video editing application with Symfony frontend and Python + FFmpeg backend, both running in Docker containers.

## Quick Start

```bash
# Build and start all containers
docker-compose up --build

# Frontend: http://localhost:8080
# Backend API: http://localhost:8000
# MySQL: localhost:3306
```

## Architecture

- **Frontend**: Symfony 7 (PHP 8.3) with Nginx
- **Backend**: Python 3.11 + FastAPI + FFmpeg
- **Database**: MySQL 8.0
- **Shared Storage**: Docker volume for video files

## Project Structure

```
stinercut3/
├── docker/
│   ├── frontend/
│   │   ├── Dockerfile
│   │   └── nginx.conf
│   └── backend/
│       └── Dockerfile
├── frontend/          # Symfony application (to be initialized)
├── backend/           # Python FastAPI application (to be created)
│   └── requirements.txt
├── docker-compose.yml
└── TODO.md           # Detailed implementation roadmap
```

## Next Steps

See `TODO.md` for the complete implementation roadmap including:
- Symfony project initialization
- Backend API development
- Video processing features
- Database schema setup
- Frontend UI development
- WebSocket integration

## Development

### Docker Commands

Use PyCharm's integrated terminal (**View** → **Tool Windows** → **Terminal**) or your system terminal:

```bash
# Start all services in background
docker-compose up -d

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f backend

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build
```

### Frontend Setup
```bash
docker-compose exec frontend bash
symfony new . --webapp --version=7.0
composer install
npm install
```

### Backend Setup
```bash
docker-compose exec backend bash
# Dependencies already installed via requirements.txt
# Create main.py and implement API endpoints
```

### Database Access
```bash
docker-compose exec mysql mysql -u stiner -plocal stinercut
```

## Features (Planned)

- Video upload and management
- Timeline-based video editor
- Effects and filters (brightness, contrast, blur, etc.)
- Transitions (fade, crossfade, wipe)
- Text overlays
- Audio mixing and volume control
- Real-time processing progress via WebSocket
- Session-based workflow (no authentication required)

## Technology Stack

- **Frontend**: Symfony 7, Webpack Encore, Video.js, Stimulus
- **Backend**: FastAPI, FFmpeg-python, SQLAlchemy, WebSockets
- **Database**: MySQL 8.0
- **Container**: Docker, Docker Compose

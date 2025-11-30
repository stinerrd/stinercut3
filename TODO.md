# Stinercut - Implementation TODO

## Quick Start
```bash
# Start all containers
docker-compose up -d

# Frontend: https://stinercut.local (via Traefik)
# Backend API: https://api.stinercut.local (via Traefik)
# Backend direct: http://localhost:8002
```

## Completed Features

### Infrastructure
- [x] Docker Compose setup (frontend, backend, mysql)
- [x] Traefik reverse proxy integration
- [x] Shared video volume between services
- [x] MySQL 8.0 database (stinercut)

### Frontend (Symfony + Eloquent)
- [x] Symfony 7 with PHP 8.3
- [x] AdminLTE 3 dashboard template
- [x] Webpack Encore asset compilation
- [x] Eloquent ORM with models (Project, Video, Job, Asset, Setting, TandemMaster)
- [x] Database migrations
- [x] HomeController with dashboard
- [x] SettingsController for app configuration
- [x] TandemMastersController for tandem master management
- [x] WebSocket client for real-time updates
- [x] Favicon

### Backend (FastAPI + Python)
- [x] FastAPI application
- [x] SQLAlchemy models (Project, Video, Job, Asset, Setting)
- [x] WebSocket hub for real-time communication
- [x] Service control API (detector start/stop)
- [x] Health check endpoint

### Detector Service
- [x] Video detection on Linux host
- [x] HTTP control API
- [x] WebSocket integration with backend

## In Progress

### add-tandem-master-tool (40/43 tasks)
- [x] TandemMaster model and migration
- [x] CRUD controller and views
- [ ] Remaining UI polish

### add-configuration (Complete - needs archive)
### add-detector-control (Complete - needs archive)
### add-detector-dashboard-widget (Complete - needs archive)
### add-media-detection-host (Complete - needs archive)
### add-websocket-events (Complete - needs archive)

## Pending Features

### Core Video Processing
- [ ] add-video-upload (0/30) - Upload videos to projects
- [ ] add-video-processing (0/25) - FFmpeg operations (trim, cut, concat)
- [ ] add-intro-outro (0/29) - Add intro/outro to videos
- [ ] add-watermarks (0/30) - Overlay watermarks
- [ ] add-transitions (0/22) - Video transitions
- [ ] add-audio-compilation (0/29) - Audio mixing and processing

### Asset Management
- [ ] add-asset-management (0/29) - Manage reusable assets (intros, outros, watermarks)

### Detection & Automation
- [ ] add-media-detection-backend (0/31) - Backend media detection
- [ ] add-media-detection-frontend (0/30) - Frontend detection UI
- [ ] add-media-detection-host-win (0/37) - Windows host detection
- [ ] add-freefall-detection (0/24) - Detect freefall in videos

### Real-time & Progress
- [ ] add-realtime-progress (0/30) - Job progress via WebSocket

### Testing
- [ ] add-backend-testing (0/33) - pytest for backend
- [ ] add-frontend-testing (0/26) - PHPUnit for frontend

### Polish
- [ ] add-polish (0/49) - UI/UX improvements, error handling

## Development Commands

### Docker
```bash
docker-compose up -d              # Start services
docker-compose logs -f backend    # View backend logs
docker-compose restart backend    # Restart backend
docker-compose down -v            # Stop and remove volumes
```

### Frontend
```bash
docker-compose exec frontend bash
composer install                  # Install PHP deps
php bin/console eloquent:migrate  # Run migrations
php bin/console cache:clear       # Clear cache
npm run dev                       # Build assets
npm run watch                     # Watch mode
```

### Backend
```bash
docker-compose exec backend bash
pip install -r requirements.txt   # Install Python deps
```

### Database
```bash
docker-compose exec -T mysql mysql -u stiner -plocal stinercut
```

## OpenSpec Workflow

```bash
openspec list                     # List active changes
openspec list --specs             # List specifications
openspec show <change-id>         # View change details
openspec validate <id> --strict   # Validate change
openspec archive <id> --yes       # Archive completed change
```

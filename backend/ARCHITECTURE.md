# Backend Architecture

Video processing backend built with Python 3.11, FastAPI, and FFmpeg.

## Directory Structure

```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # SQLAlchemy configuration and session management
├── requirements.txt     # Python dependencies
├── models/              # SQLAlchemy ORM models
│   ├── __init__.py      # Model exports
│   ├── project.py       # Video editing projects
│   ├── video.py         # Video file metadata
│   ├── job.py           # Processing job tracking
│   ├── asset.py         # Reusable assets (intros, outros, watermarks)
│   └── setting.py       # Application settings
└── routers/             # FastAPI route handlers
    ├── __init__.py
    ├── services.py      # Service control (detector restart)
    ├── websocket.py     # Real-time WebSocket hub
    └── fonts.py         # TTF/OTF to SVG font conversion
```

## Core Components

### Application Entry (`main.py`)

- FastAPI app with lifespan manager for database initialization
- CORS middleware configured for frontend origins
- Health check endpoints at `/` and `/api/health`
- Router registration for services, websocket, and fonts

### Database Layer (`database.py`)

- SQLAlchemy engine with PyMySQL driver
- Connection pool: 5 base, 10 overflow, pre-ping enabled
- Session factory with dependency injection via `get_db()`
- Declarative base for ORM models

## Data Models

### Project
Primary entity for video editing projects.
- Status: `draft` | `processing` | `completed` | `error`
- Relationships: has many Videos, has many Jobs
- Settings stored as JSON text

### Video
Video file metadata within a project.
- File info: filename, path (relative to /shared-videos/)
- Metadata: duration, width, height, codec, fps
- Editing: order, in_point, out_point for timeline trimming

### Job
Processing/rendering job tracker.
- Status: `pending` | `processing` | `completed` | `failed` | `cancelled`
- Progress: 0-100 percentage
- Timestamps: started_at, completed_at
- Result: output_path, error_message

### Asset
Reusable media assets.
- Types: `intro` | `outro` | `watermark` | `audio` | `audio_freefall` | `pax_template`
- Path relative to /shared-videos/

### Setting
Application configuration (managed via frontend).
- Types: `string` | `integer` | `boolean` | `json`
- Categorized settings with labels and descriptions

## API Routers

### Services (`/api/services`)
- `POST /detector/restart` - Restart detector service via HTTP control API

### WebSocket (`/ws`)
Unified hub for real-time communication.
- Client types: `frontend`, `detector`
- Message routing based on target field
- Message format:
  ```json
  {
    "command": "namespace:action",
    "sender": "frontend|detector|backend",
    "target": "all|frontend|detector",
    "data": {}
  }
  ```

### Fonts (`/api/fonts`)
- `POST /convert` - Convert TTF/OTF fonts to SVG path definitions
- Supports A-Z, a-z, 0-9, German umlauts (ÖÄÜöäüß)
- Target height: 60px

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.104.1 | Web framework |
| uvicorn | 0.24.0 | ASGI server |
| sqlalchemy | 2.0.23 | ORM |
| pymysql | 1.1.0 | MySQL driver |
| ffmpeg-python | 0.2.0 | FFmpeg wrapper |
| websockets | 12.0 | WebSocket support |
| httpx | 0.27.0 | Async HTTP client |
| fonttools | 4.47.0 | Font processing |
| pillow | 10.1.0 | Image processing |
| pydantic | 2.5.0 | Data validation |

## External Integrations

### Database
- MySQL 8.0 at `mysql:3306` (internal)
- Database: `stinercut`
- Credentials: `stiner` / `local`

### Shared Storage
- Volume: `/shared-videos/`
- Subdirectories: `uploads/`, `temp/`, `output/`, `thumbnails/`
- All file paths in database are relative to this mount

### Detector Service
- HTTP control API at `DETECTOR_URL` (default: `http://host.docker.internal:8001`)
- Status/enable/disable via WebSocket
- Restart via HTTP `/control/restart`

## Running

```bash
# Development (auto-reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production (single worker required for WebSocket)
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Note**: Multiple workers (`--workers N`) are not supported because the WebSocket hub
stores connections in-memory. Each worker would have its own isolated client registry,
breaking cross-client message routing. Use single worker or implement Redis Pub/Sub
for multi-worker support.

Accessible via:
- Direct: `http://localhost:8002`
- Traefik: `https://api.stinercut.local`

# Backend Architecture

## Overview

The backend is a Python 3.11 FastAPI application providing video processing, ML-based analysis, and real-time communication for the Stinercut video editing platform.

**Tech Stack:**
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn (single worker for WebSocket support)
- **Database**: SQLAlchemy 2.0 with PyMySQL (MySQL 8.0)
- **Video Processing**: FFmpeg via ffmpeg-python
- **ML Inference**: TensorFlow 2.15+ with EfficientNetB0
- **Real-time**: WebSocket hub for frontend/detector communication

## Directory Structure

```
backend/
├── main.py                    # FastAPI app initialization
├── cli.py                     # CLI commands
├── database.py                # SQLAlchemy configuration
├── requirements.txt           # Dependencies
├── models/                    # ORM models
│   ├── project.py
│   ├── video.py
│   ├── job.py
│   ├── asset.py
│   ├── setting.py
│   ├── videopart.py
│   ├── sound.py
│   ├── import_batch.py
│   ├── video_file.py
│   └── video_file_segment.py
├── routers/                   # HTTP/WebSocket handlers
│   ├── websocket.py           # Unified WebSocket hub
│   ├── services.py            # Service control endpoints
│   ├── videopart.py           # Intro/outro processing
│   ├── sound.py               # Audio processing
│   ├── video_detection.py     # ML analysis trigger
│   ├── video_splitter.py      # Video splitting
│   ├── video_slowmo.py        # Slow motion conversion
│   └── video_transition.py    # Crossfade transitions
└── services/                  # Business logic
    ├── ffmpeg_service.py      # FFmpeg operations wrapper
    ├── videopart_service.py   # Intro/outro processing
    ├── sound_service.py       # Audio processing
    ├── video_splitter.py      # Keyframe-based splitting
    ├── video_slowmo.py        # Slow motion conversion
    ├── video_transition.py    # Crossfade transitions
    └── video_analyzer/        # ML analysis pipeline
        ├── analyzer.py        # Main orchestrator
        ├── ml_classifier.py   # EfficientNetB0 classifier
        ├── segment_detector.py # Segment boundary detection
        └── jump_resolver.py   # QR + jump resolution
```

## Services

### FFmpegService

Core video/audio operations wrapper (`services/ffmpeg_service.py`):

| Method | Description |
|--------|-------------|
| `get_duration()` | Video duration via ffprobe |
| `get_video_info()` | Full metadata (duration, resolution, codec, FPS) |
| `get_video_encoding_params()` | Detailed encoding params for re-encoding |
| `get_audio_info()` | Audio stream info (codec, sample rate, channels) |
| `get_keyframes()` | Extract all keyframe timestamps |
| `find_nearest_keyframe()` | Snap timestamp to nearest keyframe |
| `extract_frame()` | PNG frame at timestamp |
| `extract_thumbnail_jpeg()` | JPEG thumbnail with quality control |
| `split_video_segment()` | Stream copy extraction (no re-encoding) |
| `convert_to_slowmo()` | Slow motion with PTS adjustment |
| `create_xfade_transition()` | Crossfade between two clips |
| `concatenate_videos()` | Concat demuxer with stream copy |
| `convert_to_wav_normalized()` | Audio normalization (EBU R128) |
| `generate_waveform_image()` | Audio waveform visualization |

### VideoAnalyzer

ML-based video classification pipeline (`services/video_analyzer/`):

**Components:**
1. **MLClassifier**: EfficientNetB0 model classifying frames into `boden`, `canopy`, `freefall`, `in_plane`
2. **SegmentDetector**: Maps ML output to segments with smoothing and boundary detection
3. **JumpResolver**: Resolves file organization based on QR codes and freefall detection

**Pipeline:**
```
Video Files → Frame Extraction → ML Classification → Segment Detection → Jump Resolution → File Organization
```

**Adaptive Sampling:**
- Coarse interval (10s) for bulk scanning
- Fine interval (1s) around detected transitions
- Reduces processing time for long videos

### VideoTransitionService

Creates fade transitions between videos (`services/video_transition.py`):

**Process:**
1. Extract part1 from file1 (stream copy)
2. Extract transition source clips from both files
3. Create crossfade with xfade filter (re-encode)
4. Extract part2 from file2 (stream copy)
5. Concatenate: part1 + transition + part2 (stream copy)

**Modes:**
- Full join (default): Creates complete merged video
- Transition only (`--transition-only`): Creates only the crossfade segment

### Other Services

| Service | Purpose |
|---------|---------|
| `VideoSplitterService` | Split video at keyframe boundaries without re-encoding |
| `VideoSlowmoService` | Convert to slow motion matching source encoding |
| `VideopartService` | Process intro/outro uploads with thumbnail extraction |
| `SoundService` | Audio processing with WAV conversion and waveform generation |

## WebSocket Communication

### Hub Architecture

Single endpoint: `/ws?client_type=frontend|detector`

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ Frontend │◄───►│ WebSocket Hub│◄───►│ Detector │
└──────────┘     └──────────────┘     └──────────┘
                        │
                        ▼
                 ┌─────────────┐
                 │   Services  │
                 └─────────────┘
```

### Message Format

```json
{
  "command": "namespace:action",
  "sender": "frontend|detector|backend",
  "target": "all|frontend|detector|backend",
  "data": {},
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### Commands

| Command | Direction | Description |
|---------|-----------|-------------|
| `videopart:uploaded` | frontend→backend | Process intro/outro upload |
| `sound:uploaded` | frontend→backend | Process audio upload |
| `videofile:start_detection` | frontend→backend | Start ML analysis |
| `gopro:copy_completed` | detector→backend | Auto-trigger analysis |
| `video:split` | frontend→backend | Split at keyframes |
| `video:slowmo` | frontend→backend | Convert to slow motion |
| `video:transition` | frontend→backend | Create crossfade |

### Progress Events

Each async operation broadcasts progress:

```
video:transition_started → video:extracting_part1 → video:extracting_transition_clips
    → video:creating_crossfade → video:concatenating → video:transition_completed
```

## Database Models

### Entity Relationships

```
Project ─────┬───── Videos
             └───── Jobs

ImportBatch ─────── VideoFiles ─────── VideoFileSegments

Assets (standalone): intro, outro, watermark, audio
Settings (standalone): key-value configuration
Videoparts (standalone): intro/outro segments
Sounds (standalone): audio files with waveforms
```

### Key Models

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Project` | Video editing project | status, name, settings |
| `Video` | Video in project | in_point, out_point, order |
| `Job` | Processing job | status, progress, error_message |
| `ImportBatch` | Analysis batch | status, resolution_type |
| `VideoFile` | Imported video | dominant_classification, qr_content |
| `VideoFileSegment` | Classified segment | classification, start_time, end_time |

## CLI Commands

```bash
# Video analysis
python cli.py detect input/folder [-w 4] [-c 10] [-f 1] [--no-adaptive] [-v]

# List import batches
python cli.py list [--status pending|analyzing|resolved|needs_manual|error]

# Split video at keyframes
python cli.py split video.mp4 -t 30 60 90 [-o output/] [-v]

# Convert to slow motion
python cli.py slowmo video.mp4 [-s 0.5] [-o output/] [-v]

# Create fade transition
python cli.py transition file1.mp4 file2.mp4 [-t 1.0] [-o output/] [--transition-only] [-v]
```

## File Storage

```
/videodata/
├── input/                    # Import batches
│   └── {batch_uuid}/
│       ├── video1.mp4
│       └── video2.mp4
├── media/
│   ├── videoparts/           # Intro/outro segments
│   │   └── intro_xxx.mp4
│   └── sounds/               # Audio files
│       └── boden_xxx.wav
└── workloads/                # Organized after analysis
    └── {workload_uuid}/
        └── videos...
```

**Path Conventions:**
- Database stores relative paths: `input/abc123/video.mp4`
- Full path: `/videodata/` + relative path
- Security: `..` traversal blocked in all services

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/health` | GET | Detailed health (DB, FFmpeg, storage) |
| `/api/services/detector/restart` | POST | Restart detector service |
| `/api/fonts/convert` | POST | TTF/OTF to SVG conversion |
| `/api/detectqr/detect` | POST | QR code detection in frame |
| `/ws` | WS | Unified WebSocket hub |

## Architectural Patterns

1. **Service Layer**: Business logic in specialized services
2. **Async Processing**: Long operations via `asyncio.create_task()`
3. **Thread Pool**: FFmpeg calls in `asyncio.to_thread()` to avoid blocking
4. **Progress Callbacks**: Real-time WebSocket updates during operations
5. **Stream Copy**: Splitting/concatenation without re-encoding where possible
6. **Lazy Loading**: ML model loads on first classification request
7. **Dependency Injection**: Services accept optional dependencies for testing

## Configuration

Environment variables via `.env`:

```bash
DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/stinercut
VIDEODATA_PATH=/videodata
SHARED_VIDEOS_PATH=/shared-videos
```

## Dependencies

**Core:**
- fastapi, uvicorn, sqlalchemy, pymysql, pydantic

**Video:**
- ffmpeg-python, opencv-python-headless, pillow

**ML:**
- tensorflow, numpy, pyzbar

**Utilities:**
- websockets, httpx, aiofiles, python-multipart

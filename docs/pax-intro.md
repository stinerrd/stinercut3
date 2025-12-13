# PAX Screen Intro Feature

Creates animated welcome screen videos for tandem skydiving passengers.

## Overview

- Generates personalized intro videos from SVG templates with animated text
- Text animation sequence: empty -> name -> "in" -> "in the" -> "in the sky" -> empty
- Drop shadow with Gaussian blur effect on text
- Dynamic frame timing that matches audio duration automatically

## Quick Start

### CLI Command

```bash
docker-compose exec -T backend python cli.py pax-intro \
  --name "Passenger Name" \
  --template-id 11 \
  --font-id 12 \
  --audio-id 8 \
  --output /videodata/output/pax_test \
  -v
```

### WebSocket Command

```json
{
  "command": "video:pax_intro",
  "sender": "frontend",
  "target": "backend",
  "data": {
    "pax_name": "Passenger Name",
    "template_id": 11,
    "font_id": 12,
    "audio_id": 8,
    "output_path": "/videodata/output/pax_test",
    "video_dimensions": {
      "width": 1920,
      "height": 1080,
      "fps": 30
    }
  }
}
```

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| pax_name / --name | string | Yes | - | Passenger name to display |
| template_id | int | Yes | - | ID of splashscreen (category='image') |
| font_id | int | Yes | - | ID of splashscreen (category='font') |
| audio_id | int | Yes | - | ID of sound record |
| output_path / --output | string | Yes | - | Output directory path |
| width | int | No | 1920 | Video width in pixels |
| height | int | No | 1080 | Video height in pixels |
| fps | int | No | 30 | Frame rate |
| codec | string | No | libx264 | Video codec |

## Frame Sequence

Frames are weighted and scaled to match audio duration:

| Frame | Weight | Description |
|-------|--------|-------------|
| p0 | 0.5 | Empty template (intro) |
| p1 | 1.0 | PAX name only |
| p2 | 0.5 | Name + "in" |
| p3 | 0.5 | Name + "in the" |
| p4 | 3.0 | Name + "in the sky" (main frame) |
| p0_end | 1.0 | Empty template (outro) |

**Total Weight: 6.5**

Example: For 13-second audio, p4 displays for ~6 seconds (3.0/6.5 * 13).

## Database Resources

### splashscreen table

- **category='image'**: SVG templates with placeholders
  - `[[[WIDTH]]]` - Video width
  - `[[[HEIGHT]]]` - Video height
  - `[[[TEXT]]]` - Generated text content
  - `[[[FONT]]]` - Font definitions

- **category='font'**: SVG font definitions
  - Character paths like `<path id="_A" d="..."/>`
  - Special characters: `_auml` (a), `_ouml` (o), `_uuml` (u), `_szlig` (ß)

### sound table

Audio files stored in `/videodata/media/sounds/`

## Progress Events

The service emits these WebSocket events:

| Event | Description |
|-------|-------------|
| `video:pax_intro_started` | Processing started |
| `video:fetched_resources` | Template, font, audio loaded |
| `video:creating_frame` | Each frame being generated |
| `video:rendering_video` | FFmpeg video creation |
| `video:pax_intro_completed` | Success with output path |
| `video:pax_intro_error` | Error with message |

## Technical Details

### Dependencies

- **rsvg-convert** (librsvg2-bin): SVG to PNG conversion with filter support
- **ffmpeg-python**: Video generation
- **ffprobe**: Audio duration detection

### Drop Shadow Filter

```xml
<filter id="drop-shadow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur"/>
    <feOffset in="blur" dx="6" dy="6" result="offsetBlur"/>
</filter>
```

### Text Positioning

| Property | Value | Description |
|----------|-------|-------------|
| First line X | 80 | Name X position |
| First line Y | 500 | Name Y position |
| First line scale | 2.0 | Name size multiplier |
| Second line X | 80 | Phrase X position |
| Second line Y | 650 | Phrase Y position |
| Second line scale | 1.0 | Phrase size multiplier |

## Files

| File | Description |
|------|-------------|
| `backend/services/pax_screen_service.py` | Core service |
| `backend/routers/pax_intro.py` | WebSocket handler |
| `backend/routers/websocket.py` | WebSocket hub routing |
| `backend/models/splashscreen.py` | Database model |
| `backend/cli.py` | CLI command |
| `docker/backend/Dockerfile` | Added librsvg2-bin |

## Troubleshooting

### Template/Font not found
- Verify ID exists: `SELECT * FROM splashscreen WHERE id = <id>;`
- Check category is 'image' or 'font'

### Audio file not found
- Check file path: `SELECT file_path FROM sound WHERE id = <id>;`
- Verify file exists: `ls -l /videodata/media/sounds/<path>`

### Text not appearing
- Check template has `[[[TEXT]]]` placeholder
- Verify font contains all characters in name

### Drop shadow clipped
- Filter region should be `-50%` to `200%`
- Check template viewBox dimensions

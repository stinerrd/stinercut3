# Detector Service Architecture

## Overview

The Stinercut Detector is a standalone Python service that monitors USB device events and automatically imports video files from GOPRO cameras. It runs on the host system (not in Docker) to access physical USB devices.

## Components

```
detector/
├── stinercut_detector.py     # Main service (single file)
├── stinercut-detector.service       # Systemd unit
├── stinercut-detector-watcher.path  # File monitor trigger
├── stinercut-detector-watcher.service
├── 50-stinercut-detector.rules      # Polkit rules
└── config.ini                       # Configuration
```

## Core Classes

### StinercutDetector

Main service class that:
- Monitors udev block subsystem for USB device add/remove events
- Auto-mounts removable media with appropriate filesystem options
- Detects GOPRO devices by DCIM/xxxGOPRO folder pattern
- Maintains WebSocket connection to backend for real-time notifications
- Provides HTTP control server for service management

### GoproCopyManager

Manages GOPRO file copy operations:
- Scans DCIM folders for GOPRO video files (.mp4, .lrv)
- Copies files using rsync with progress tracking
- Implements duplicate detection via `_stinercut_copied.txt` log
- Fixes file permissions (644 for files, 755 for directories)
- Organizes SD card by renaming DCIM to UUID after import

### CopyJob (dataclass)

Represents a single copy operation with:
- Job ID (UUID)
- Device and mount information
- File list and progress tracking
- Error state

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   SD Card       │     │    Detector      │     │    Backend      │
│   (GOPRO)       │     │    Service       │     │    (FastAPI)    │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         │  USB Insert           │                        │
         │──────────────────────>│                        │
         │                       │                        │
         │                       │  gopro.detected        │
         │                       │───────────────────────>│
         │                       │                        │
         │  rsync copy           │                        │
         │<─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─>│                        │
         │                       │                        │
         │                       │  gopro.copy_progress   │
         │                       │───────────────────────>│
         │                       │                        │
         │                       │  gopro.copy_completed  │
         │                       │───────────────────────>│
         │                       │                        │
         │  rename DCIM→UUID     │                        │
         │<──────────────────────│                        │
         │                       │                        │
         │                       │  gopro.sd_organized    │
         │                       │───────────────────────>│
         │                       │                        │
```

## WebSocket Signals

### Outgoing (Detector → Backend)

| Signal | Description |
|--------|-------------|
| `gopro.detected` | GOPRO device detected with video files |
| `gopro.copy_started` | Copy operation initiated |
| `gopro.copy_progress` | Progress update (10% intervals) |
| `gopro.copy_completed` | Files copied to HDD successfully |
| `gopro.copy_failed` | Copy operation failed |
| `gopro.sd_organized` | DCIM renamed to UUID on SD card |
| `gopro.sd_organize_failed` | SD card rename failed |
| `device.mounted` | Non-GOPRO device mounted |
| `device.unmounted` | Device unmounted |

### Incoming (Backend → Detector)

| Command | Description |
|---------|-------------|
| `detector:status` | Request current status |
| `detector:enable` | Enable device listener |
| `detector:disable` | Disable device listener |

## File Storage

### SD Card Structure (After Import)

```
/media/user/SDCARD/
└── abc123-def456-...        # Renamed from DCIM (UUID)
    ├── _stinercut_copied.txt    # Copy log (moves with DCIM rename)
    ├── 100GOPRO/
    │   ├── GX010001.MP4
    │   └── GL010001.LRV
    └── 101GOPRO/
        └── ...
```

### Target Storage

```
/videodata/input/
└── abc123-def456-.../       # Import UUID
    ├── 100GOPRO/
    │   ├── GX010001.MP4
    │   └── GL010001.LRV
    └── 101GOPRO/
        └── ...
```

## Copy Log Format

The `_stinercut_copied.txt` file tracks imported files:

```
100GOPRO/GX010001.MP4 => abc123-def456-...
100GOPRO/GL010001.LRV => abc123-def456-...
101GOPRO/GX020001.MP4 => abc123-def456-...
```

This enables:
- Skipping already-copied files on re-insert
- UUID reuse for continued imports from same device

## Configuration

```ini
[api]
url = http://localhost:8002
ws_url = ws://localhost:8002/ws

[detector]
debounce_delay = 2.0
mount_retries = 6
mount_retry_interval = 0.5
auto_mount = true
mount_base = /media/{user}

[gopro]
auto_copy = true
target_base = /videodata/input

[control]
enabled = false
port = 8001
```

## Systemd Integration

The service runs as a user service with:
- Auto-restart on failure
- Security hardening (NoNewPrivileges, ProtectSystem)
- File watcher for configuration changes

```bash
# Service management
systemctl --user status stinercut-detector
systemctl --user restart stinercut-detector
journalctl --user -u stinercut-detector -f
```

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Device not mountable | Log warning, skip device |
| GOPRO not detected | Mount as regular device |
| Copy fails mid-transfer | Send `copy_failed`, cleanup temp files |
| SD card write-protected | Send `sd_organize_failed` with error |
| WebSocket disconnected | Queue messages, auto-reconnect |
| Backend unreachable | Continue operation, retry connection |

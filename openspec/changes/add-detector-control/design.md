# Design: Detector Service Control

## Context

The Tandem Video Editor runs in Docker containers while the detector service runs on the host system (monitoring USB devices via udev). Operations staff need to control the detector without direct host access.

**Constraints:**
- Backend runs in Docker container (isolated network)
- Detector runs on host with systemd (`Restart=always`)
- Must support Linux now, Windows later
- Minimal changes to host system preferred

## Goals / Non-Goals

**Goals:**
- Backend can enable/disable detector monitoring
- Backend can query detector status (running + monitoring enabled)
- Cross-platform HTTP API contract
- Secure communication (localhost-only by default)

**Non-Goals:**
- Starting/stopping the daemon process (systemd handles this)
- Windows implementation (future work)
- Complex authentication (optional API key suffices)

## Decisions

### Decision 1: Enable/Disable vs Start/Stop
**What:** Control monitoring state, not daemon lifecycle
**Why:**
- Systemd's `Restart=always` fights against stop commands
- Daemon always runs, but monitoring can be toggled off
- Simpler: no file-based triggers or path watchers needed
- Monitoring disabled by default for safety

**Alternatives considered:**
- Stop/start daemon: Doesn't work with `Restart=always`
- File-based start trigger: Added complexity, still has race conditions

### Decision 2: HTTP API in Detector
**What:** Add HTTP server to detector service running alongside udev monitor
**Why:**
- Reuses existing host service (no new daemons)
- Cross-platform: Windows can implement same HTTP interface
- Backend stays platform-agnostic (just HTTP calls)

**Alternatives considered:**
- D-Bus socket mount: Requires privilege escalation, Linux-only
- SSH from container: Over-engineered, key management complexity

### Decision 3: Threading for HTTP Server
**What:** Run HTTP control server in separate thread from udev monitor
**Why:**
- Both need to run concurrently
- HTTP server uses timeout-based polling for graceful shutdown
- Shares `shutdown_event` with main monitor loop

## Architecture

```
┌─────────────────────┐         HTTP          ┌──────────────────────┐
│  Backend Container  │ ──────────────────────▶│  Detector (Host)     │
│  (FastAPI)          │  POST /control/enable  │  Thread 1: udev      │
│                     │  POST /control/disable │  Thread 2: HTTP API  │
│                     │  POST /control/restart │                      │
│                     │  GET /status           │  Port 8001           │
└─────────────────────┘                        └──────────────────────┘
                                                        │
                                               monitoring_enabled flag
                                               (false by default)
                                                        │
                                                        ▼
                                               ┌──────────────────────┐
                                               │  handle_device_event │
                                               │  skips if disabled   │
                                               └──────────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Returns `running`, `monitoring_enabled`, `pending_events` |
| `/control/enable` | POST | Enable device monitoring |
| `/control/disable` | POST | Disable device monitoring |
| `/control/restart` | POST | Restart daemon (systemd handles restart) |

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| HTTP server thread crashes | Main loop catches exceptions, logs errors |
| Port 8001 conflict | Configurable via config.ini |
| Unauthorized access | Bind to 0.0.0.0 only when needed, optional API key |
| Events missed while disabled | Expected behavior, user explicitly disabled |

## Migration Plan

1. Update detector with HTTP control server and monitoring toggle
2. Update systemd service with `Restart=always`
3. Update backend with service control router (enable/disable endpoints)
4. Update docker-compose with host.docker.internal

**Rollback:** Remove HTTP control code from detector, backend endpoints return 501

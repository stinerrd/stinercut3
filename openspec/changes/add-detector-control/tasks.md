# Tasks: Add Detector Service Control

## 1. Detector HTTP Control Server

- [x] 1.1 Add `[control]` section to `detector/config.ini` (enabled, host, port, api_key)
- [x] 1.2 Add HTTP server thread to `StinercutDetector` class
- [x] 1.3 Implement `GET /status` endpoint (returns running, monitoring_enabled, pending events)
- [x] 1.4 Implement `POST /control/enable` endpoint (enables device monitoring)
- [x] 1.5 Implement `POST /control/disable` endpoint (disables device monitoring)
- [x] 1.6 Implement `POST /control/restart` endpoint (clean exit for systemd restart)
- [x] 1.7 Add `monitoring_enabled` flag (disabled by default)
- [x] 1.8 Add monitoring check in `handle_device_event()` to skip events when disabled
- [x] 1.9 Add optional API key authentication
- [x] 1.10 Update `detector/stinercut-detector.service` with `Restart=always`

## 2. Backend Service Control API

- [x] 2.1 Add `httpx` to `backend/requirements.txt`
- [x] 2.2 Create `backend/routers/services.py` with service control endpoints
- [x] 2.3 Implement `GET /api/services/detector/status`
- [x] 2.4 Implement `POST /api/services/detector/enable`
- [x] 2.5 Implement `POST /api/services/detector/disable`
- [x] 2.6 Implement `POST /api/services/detector/restart`
- [x] 2.7 Register services router in `backend/main.py`

## 3. Docker Configuration

- [x] 3.1 Add `DETECTOR_URL` environment variable to docker-compose.yml
- [x] 3.2 Add `extra_hosts` mapping for `host.docker.internal`

## 4. Testing & Documentation

- [x] 4.1 Test HTTP control endpoints manually (enable, disable, status)
- [ ] 4.2 Test backend proxy endpoints
- [ ] 4.3 Update detector README with control API documentation

## Removed Tasks (No longer needed)

The following tasks from the original design were removed as they're no longer necessary with the enable/disable approach:

- ~~Systemd path watcher for start trigger~~ (daemon always runs)
- ~~`POST /control/stop` endpoint~~ (replaced with disable)
- ~~`POST /api/services/detector/start`~~ (replaced with enable)
- ~~File-based trigger mechanism~~ (not needed)

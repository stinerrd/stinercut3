# Change: Add Detector Service Control from Backend

## Why

The backend container needs to enable/disable the detector service's device monitoring for operational control. The daemon always runs but monitoring can be toggled on/off. This avoids fighting with systemd's restart policies.

## What Changes

- Add HTTP control API to detector service (endpoints: `/status`, `/control/enable`, `/control/disable`, `/control/restart`)
- Add `monitoring_enabled` state flag to detector (disabled by default)
- Add backend API endpoints to proxy control commands to detector
- Update docker-compose to allow backend-to-host communication
- **Cross-platform design**: Same HTTP API contract for Linux (now) and Windows (future)

## Impact

- Affected specs: `detector-control` (new), `backend-api` (new endpoints)
- Affected code:
  - `detector/stinercut_detector.py` - Add HTTP control server, monitoring toggle
  - `detector/config.ini` - Add `[control]` section
  - `detector/stinercut-detector.service` - Update restart policy
  - `backend/routers/services.py` - New service control router
  - `backend/main.py` - Register services router
  - `docker-compose.yml` - Add host.docker.internal mapping

# Stinercut Media Detector

Host service that monitors USB device events and communicates with the frontend via a unified WebSocket hub.

## Requirements

- Linux with systemd
- Python 3.8+
- pyudev
- websocket-client
- Backend running with exposed port (default: 8002)

## Installation

```bash
cd detector
sudo ./install.sh [API_URL]
```

**Parameters:**
- `API_URL` - Backend API URL (default: `http://localhost:8000`)

**Example:**
```bash
sudo ./install.sh http://192.168.1.100:8000
```

The installer will:
1. Create `/opt/stinercut-detector/` with detector files
2. Install Python dependencies (pyudev, requests)
3. Create `stinercut` group and add your user to it
4. Install systemd service and polkit rule
5. Enable and start the service

**Note:** Log out and back in for group membership to take effect.

## Uninstallation

```bash
sudo ./uninstall.sh
```

To also remove logs and the stinercut group:
```bash
sudo ./uninstall.sh --purge
```

## Service Management

After installation (and re-login), no sudo required:

```bash
systemctl start stinercut-detector
systemctl stop stinercut-detector
systemctl restart stinercut-detector
systemctl status stinercut-detector
```

View logs:
```bash
journalctl -u stinercut-detector -f
```

## Configuration

Edit `/opt/stinercut-detector/config.ini`:

```ini
[api]
# WebSocket URL for backend hub (direct to Docker port, no SSL)
# client_type=detector identifies this client to the hub for message routing
websocket_url = ws://localhost:8002/ws?client_type=detector

[detector]
debounce_delay = 2.0
mount_retries = 6
mount_retry_interval = 0.5
automount = true
mount_base = /media/{user}
mount_user = stiner

[control]
enabled = true
host = 0.0.0.0
port = 8001
api_key =

[logging]
file = /var/log/stinercut/detector.log
level = INFO
```

Restart service after changes:
```bash
systemctl restart stinercut-detector
```

## Architecture

All clients connect to a single WebSocket hub at `/ws`. Messages include routing metadata for targeted delivery.

```
                    ┌─────────────────────────────────────┐
                    │     Backend WebSocket Hub (:8002)   │
                    │              /ws                    │
                    └─────────────────────────────────────┘
                           ▲                    ▲
                           │                    │
              ?client_type=detector    ?client_type=frontend
                           │                    │
                    ┌──────┴──────┐      ┌──────┴──────┐
                    │  Detector   │      │  Frontend   │
                    │   (host)    │      │  (browser)  │
                    └─────────────┘      └─────────────┘
```

### Message Format

All WebSocket messages use a unified structure:

```json
{
  "command": "namespace:action",
  "sender": "frontend|detector|backend",
  "target": "all|frontend|detector",
  "data": {}
}
```

**Fields:**
- `command`: Namespaced action (colon for commands, dot for events)
- `sender`: Who sent the message
- `target`: Who should receive (`all` = broadcast, or specific client type)
- `data`: Command-specific payload

### Commands (Frontend → Detector)

| Command | Description |
|---------|-------------|
| `detector:status` | Request current detector status |
| `detector:enable` | Enable device monitoring |
| `detector:disable` | Disable device monitoring |

### Events (Detector → Frontend)

| Event | Payload | Description |
|-------|---------|-------------|
| `detector.status` | `{running, monitoring_enabled, pending_events}` | Status update response |
| `device.mounted` | `{device_node, mount_path}` | Device was mounted |
| `device.unmounted` | `{device_node}` | Device was unmounted |

### Event Flow Example

1. User toggles monitoring switch in browser
2. Frontend sends `detector:enable` command via WebSocket
3. Hub routes message to detector client
4. Detector enables monitoring, sends `detector.status` event
5. Hub routes event to frontend client
6. Frontend updates UI with new status

## HTTP Control API (Debugging)

The HTTP API on port 8001 remains available for manual testing and debugging.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Returns service status |
| POST | `/control/enable` | Enable device monitoring |
| POST | `/control/disable` | Disable device monitoring |
| POST | `/control/restart` | Triggers service restart |

**Note:** The frontend uses WebSocket for all control operations. HTTP endpoints are for debugging with curl.

**Example:**
```bash
# Get status
curl http://localhost:8001/status

# Enable monitoring
curl -X POST http://localhost:8001/control/enable

# Disable monitoring
curl -X POST http://localhost:8001/control/disable
```

**API Key Authentication:**

If `api_key` is set in config, include it in requests:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8001/status
```

## Monitoring State

The detector starts with monitoring **disabled by default**. Device events are ignored until monitoring is explicitly enabled via WebSocket command or HTTP API. This prevents unintended operations when the service starts.

## Adding Users

To allow other users to manage the service:
```bash
sudo usermod -aG stinercut <username>
```

## How It Works

1. Connects to backend WebSocket hub as `client_type=detector`
2. Listens for commands from frontend (`detector:status`, `detector:enable`, `detector:disable`)
3. Monitors udev events for block devices (USB drives, SD cards)
4. Filters for partition mount events
5. When monitoring is enabled and device events occur:
   - Resolves mount point from `/proc/mounts`
   - Sends `device.mounted` or `device.unmounted` events via WebSocket
   - Hub routes events to frontend clients

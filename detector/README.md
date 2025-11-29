# Stinercut Media Detector

Host service that monitors USB device events and notifies the backend when removable media is mounted or unmounted.

## Requirements

- Linux with systemd
- Python 3.8+
- pyudev
- Backend API running (for notifications)

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
url = http://localhost:8000

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

## HTTP Control API

When `[control]` is enabled, the detector exposes an HTTP API for remote management.

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/status` | Returns service status (running, monitoring_enabled, pending_events) |
| POST | `/control/enable` | Enable device monitoring |
| POST | `/control/disable` | Disable device monitoring |
| POST | `/control/restart` | Triggers restart (systemd will restart the service) |

**Monitoring State:**

The detector starts with monitoring **disabled by default**. Device events are ignored until monitoring is explicitly enabled via the API. This prevents unintended operations when the service starts.

**Example:**
```bash
# Get status
curl http://localhost:8001/status
# Response: {"running": true, "monitoring_enabled": false, "pending_events": 0, "service": "stinercut-detector"}

# Enable monitoring
curl -X POST http://localhost:8001/control/enable
# Response: {"status": "enabled", "monitoring_enabled": true}

# Disable monitoring
curl -X POST http://localhost:8001/control/disable
# Response: {"status": "disabled", "monitoring_enabled": false}

# Restart service
curl -X POST http://localhost:8001/control/restart
```

**API Key Authentication:**

If `api_key` is set in config, include it in requests:
```bash
curl -H "X-API-Key: your-secret-key" http://localhost:8001/status
```

## Adding Users

To allow other users to manage the service:
```bash
sudo usermod -aG stinercut <username>
```

## How It Works

1. Monitors udev events for block devices (USB drives, SD cards)
2. Filters for partition mount events
3. Resolves mount point from `/proc/mounts`
4. Sends POST request to backend API:
   - `POST /api/devices/mount` with `{device_node, mount_path}`
   - `POST /api/devices/unmount` with `{device_node}`

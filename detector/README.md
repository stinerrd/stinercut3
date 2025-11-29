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

[logging]
file = /var/log/stinercut/detector.log
level = INFO
```

Restart service after changes:
```bash
systemctl restart stinercut-detector
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

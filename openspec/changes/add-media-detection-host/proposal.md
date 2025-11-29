# Change: Add Media Detection Host Service

## Why
The web application needs to know when removable media (SD cards, USB drives) is connected to the Linux host. A host-level service can detect device events and notify the backend, enabling the application to react to newly connected media.

## What Changes
- Create host-level Python daemon using pyudev for USB device monitoring
- Automount removable media when detected
- Send mount/unmount events with mount point path to backend API
- Create systemd service for automatic startup and management
- No media content analysis - just device events with mount paths

## Impact
- Affected specs: `media-detection-host` (new capability)
- Affected code:
  - `detector/` - New host service directory
  - `detector/stinercut_detector.py` - Main daemon script
  - `detector/stinercut-detector.service` - systemd unit file
  - `detector/requirements.txt` - Python dependencies (pyudev, requests)
  - `detector/install.sh` - Installation script

## Dependencies
- Requires: None (standalone host service)
- Required by: `add-media-detection-backend` (receives events)

## Reference
Based on pyudev device monitoring pattern from original stinercut `stinercut_listener.py`.

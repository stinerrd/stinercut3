# Change: Add Media Detection Host Service (Windows 11)

## Why
The web application needs to know when removable media (SD cards, USB drives) is connected to the Windows 11 host. A host-level service can detect device events via WMI and notify the backend, enabling the application to react to newly connected media.

## What Changes
- Create host-level Python application using WMI for USB volume monitoring
- Monitor Win32_VolumeChangeEvent for drive insertion/removal
- Send mount/unmount events with drive letter path to backend API
- Create Windows Service (or Task Scheduler task) for automatic startup
- No media content analysis - just device events with drive paths

## Impact
- Affected specs: `media-detection-host-win` (new capability)
- Affected code:
  - `detector-win/` - New Windows host service directory
  - `detector-win/stinercut_detector_win.py` - Main service script
  - `detector-win/requirements.txt` - Python dependencies (wmi, requests)
  - `detector-win/install.ps1` - PowerShell installation script
  - `detector-win/service_wrapper.py` - Windows Service wrapper (pywin32)

## Dependencies
- Requires: None (standalone host service)
- Required by: `add-media-detection-backend` (receives events)

## Differences from Linux Version
| Aspect | Linux | Windows 11 |
|--------|-------|------------|
| Detection API | pyudev (netlink) | WMI (Win32_VolumeChangeEvent) |
| Mount Path | /media/user/device | D:\, E:\ (drive letters) |
| Service Type | systemd | Windows Service (pywin32) |
| Packages | pyudev, requests | wmi, pywin32, requests |
| Install Script | bash + systemctl | PowerShell + sc.exe |

## Reference
Based on WMI device monitoring pattern using Win32_VolumeChangeEvent.

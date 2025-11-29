## 1. Project Structure
- [ ] 1.1 Create `detector-win/` directory in project root
- [ ] 1.2 Create `detector-win/requirements.txt` with wmi, pywin32, requests
- [ ] 1.3 Create `detector-win/config.ini` for configuration

## 2. WMI Volume Monitoring
- [ ] 2.1 Create `detector-win/stinercut_detector_win.py` main script
- [ ] 2.2 Implement WMI Win32_VolumeChangeEvent watcher
- [ ] 2.3 Filter EventType=2 (device arrival) and EventType=3 (device removal)
- [ ] 2.4 Implement event debouncing (2-second delay)
- [ ] 2.5 Add logging configuration

## 3. Drive Letter Resolution
- [ ] 3.1 Query Win32_LogicalDisk for removable drives (DriveType=2)
- [ ] 3.2 Map volume events to drive letters
- [ ] 3.3 Add retry logic for delayed drive letter assignment
- [ ] 3.4 Handle removed drives gracefully

## 4. Backend API Communication
- [ ] 4.1 Implement HTTP POST to /api/devices/mount on drive arrival
- [ ] 4.2 Implement HTTP POST to /api/devices/unmount on drive removal
- [ ] 4.3 Include device_node (volume serial) and mount_path (drive letter) in request body
- [ ] 4.4 Handle API connection errors with logging

## 5. Windows Service
- [ ] 5.1 Create `detector-win/service_wrapper.py` using pywin32
- [ ] 5.2 Implement win32serviceutil.ServiceFramework subclass
- [ ] 5.3 Configure service name and display name
- [ ] 5.4 Implement SvcDoRun and SvcStop methods
- [ ] 5.5 Add service recovery options (restart on failure)

## 6. Installation
- [ ] 6.1 Create `detector-win/install.ps1` PowerShell script
- [ ] 6.2 Install Python dependencies via pip
- [ ] 6.3 Register Windows Service using sc.exe or pywin32
- [ ] 6.4 Set service to auto-start
- [ ] 6.5 Start service

## 7. Configuration
- [ ] 7.1 Configure backend API URL in config.ini
- [ ] 7.2 Configure log file path (e.g., %APPDATA%\StinercutDetector\)
- [ ] 7.3 Configure debounce delay

## 8. Verification
- [ ] 8.1 Test with USB device insertion
- [ ] 8.2 Test with USB device removal
- [ ] 8.3 Verify API calls include correct drive letter
- [ ] 8.4 Test service restart recovery
- [ ] 8.5 Test with SD card reader

## 9. Alternative: Tray Application
- [ ] 9.1 (Optional) Create system tray version using pystray
- [ ] 9.2 (Optional) Show notification on device events
- [ ] 9.3 (Optional) Provide manual scan option

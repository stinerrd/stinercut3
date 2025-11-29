## 1. Project Structure
- [x] 1.1 Create `detector/` directory in project root
- [x] 1.2 Create `detector/requirements.txt` with pyudev, requests
- [x] 1.3 Create `detector/config.ini` for configuration

## 2. Device Detection Daemon
- [x] 2.1 Create `detector/stinercut_detector.py` main script
- [x] 2.2 Implement pyudev.Monitor for block device events
- [x] 2.3 Filter for device_type='partition' events
- [x] 2.4 Implement event debouncing (2-second delay)
- [x] 2.5 Add logging configuration

## 3. Mount Point Resolution
- [x] 3.1 Implement mount point lookup from /proc/mounts
- [x] 3.2 Add retry logic for delayed mounts (6 retries, 0.5s interval)
- [x] 3.3 Handle unmounted devices gracefully

## 4. Backend API Communication
- [x] 4.1 Implement HTTP POST to /api/devices/mount on device add
- [x] 4.2 Implement HTTP POST to /api/devices/unmount on device remove
- [x] 4.3 Include device_node and mount_path in request body
- [x] 4.4 Handle API connection errors with logging

## 5. Systemd Service
- [x] 5.1 Create `detector/stinercut-detector.service` unit file
- [x] 5.2 Configure After=network.target dependency
- [x] 5.3 Set Restart=on-failure policy
- [x] 5.4 Configure user/group for service execution

## 6. Installation
- [x] 6.1 Create `detector/install.sh` script
- [x] 6.2 Install Python dependencies
- [x] 6.3 Copy service file to /etc/systemd/system/
- [x] 6.4 Enable and start service

## 7. Configuration
- [x] 7.1 Configure backend API URL in config.ini
- [x] 7.2 Configure log file path
- [x] 7.3 Configure debounce delay

## 8. Verification
- [x] 8.1 Test with USB device insertion
- [x] 8.2 Test with USB device removal
- [x] 8.3 Verify API calls are made correctly
- [x] 8.4 Test service restart recovery

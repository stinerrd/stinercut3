## 1. Media Scanner Service
- [ ] 1.1 Create `backend/services/media_scanner.py`
- [ ] 1.2 Implement GoPro folder detection (DCIM/[0-9]*GOPRO pattern)
- [ ] 1.3 Implement .MP4 file counting in GoPro folders
- [ ] 1.4 Implement .JPG file counting in GoPro folders
- [ ] 1.5 Implement media type classification (video/photo/multi/empty)
- [ ] 1.6 Return scan results as structured data

## 2. Device API Endpoints
- [ ] 2.1 Create `backend/routers/devices.py` with FastAPI router
- [ ] 2.2 Implement `POST /api/devices/mount` - Handle mount notification
- [ ] 2.3 Implement `POST /api/devices/unmount` - Handle unmount notification
- [ ] 2.4 Implement `GET /api/devices` - List connected devices
- [ ] 2.5 Implement `GET /api/devices/{device_id}` - Get device details

## 3. Device Storage
- [ ] 3.1 Create in-memory device store (dict by device_node)
- [ ] 3.2 Store: device_id, device_node, mount_path, media_type, video_count, photo_count, detected_at
- [ ] 3.3 Add device on mount notification
- [ ] 3.4 Remove device on unmount notification
- [ ] 3.5 Handle duplicate mount notifications gracefully

## 4. WebSocket Broadcasting
- [ ] 4.1 Create WebSocket manager for device events
- [ ] 4.2 Broadcast "device_added" event when device is mounted and scanned
- [ ] 4.3 Broadcast "device_removed" event when device is unmounted
- [ ] 4.4 Include full device details in broadcast messages

## 5. Router Registration
- [ ] 5.1 Import devices router in main.py
- [ ] 5.2 Register router with prefix /api/devices
- [ ] 5.3 Add WebSocket endpoint /ws/devices

## 6. Docker Volume Configuration
- [ ] 6.1 Update docker-compose.yml to mount /media from host
- [ ] 6.2 Ensure backend container can read host mount points
- [ ] 6.3 Document volume mount requirements

## 7. Verification
- [ ] 7.1 Test mount notification creates device record
- [ ] 7.2 Test GoPro folder detection on real device
- [ ] 7.3 Test media classification accuracy
- [ ] 7.4 Test unmount removes device record
- [ ] 7.5 Test WebSocket broadcasts reach clients

## ADDED Requirements

### Requirement: Mount Event Handling
The system SHALL handle mount/unmount notifications from the host service.

#### Scenario: Mount notification received
- **WHEN** POST /api/devices/mount is called with device_node and mount_path
- **THEN** the system scans the mount path and registers the device

#### Scenario: Unmount notification received
- **WHEN** POST /api/devices/unmount is called with device_node
- **THEN** the system removes the device from connected devices

#### Scenario: Duplicate mount notification
- **WHEN** mount notification is received for already-registered device
- **THEN** the system updates the existing device record

### Requirement: GoPro Folder Detection
The system SHALL identify GoPro media by folder structure.

#### Scenario: Standard GoPro structure
- **WHEN** mount path contains DCIM/100GOPRO/ folder
- **THEN** the system identifies device as containing GoPro media

#### Scenario: Multiple GoPro folders
- **WHEN** mount path contains DCIM/100GOPRO/, DCIM/101GOPRO/, etc.
- **THEN** the system scans all matching folders

#### Scenario: Folder pattern matching
- **WHEN** scanning DCIM directory
- **THEN** folders matching pattern `[0-9]*GOPRO` (case-insensitive) are detected

#### Scenario: Non-GoPro device
- **WHEN** mount path has no DCIM/[0-9]*GOPRO/ structure
- **THEN** device is registered with media_type "none"

### Requirement: Media Classification
The system SHALL classify media type based on file contents.

#### Scenario: Video only
- **WHEN** GoPro folders contain only .MP4 files
- **THEN** media_type is "video"

#### Scenario: Photo only
- **WHEN** GoPro folders contain only .JPG files
- **THEN** media_type is "photo"

#### Scenario: Mixed media
- **WHEN** GoPro folders contain both .MP4 and .JPG files
- **THEN** media_type is "multi"

#### Scenario: Empty GoPro folders
- **WHEN** GoPro folders contain no .MP4 or .JPG files
- **THEN** media_type is "empty"

### Requirement: Media File Counting
The system SHALL count media files on detected devices.

#### Scenario: Count videos
- **WHEN** device is scanned
- **THEN** total count of .MP4 files across all GoPro folders is stored

#### Scenario: Count photos
- **WHEN** device is scanned
- **THEN** total count of .JPG files across all GoPro folders is stored

### Requirement: Device List API
The system SHALL provide API for listing connected devices.

#### Scenario: List all devices
- **WHEN** GET /api/devices is called
- **THEN** list of all connected devices with details is returned

#### Scenario: Get single device
- **WHEN** GET /api/devices/{device_id} is called
- **THEN** details of specified device are returned

#### Scenario: Device not found
- **WHEN** GET /api/devices/{device_id} is called for unknown device
- **THEN** 404 Not Found is returned

### Requirement: Device Data Structure
The system SHALL store device information with required fields.

#### Scenario: Device record fields
- **WHEN** device is registered
- **THEN** record contains: device_id, device_node, mount_path, media_type, video_count, photo_count, detected_at

#### Scenario: Device ID generation
- **WHEN** new device is registered
- **THEN** unique device_id is generated (UUID or hash of device_node)

### Requirement: WebSocket Broadcasting
The system SHALL broadcast device events via WebSocket.

#### Scenario: Device added broadcast
- **WHEN** device is successfully registered and scanned
- **THEN** WebSocket message with type "device_added" and device details is broadcast

#### Scenario: Device removed broadcast
- **WHEN** device is removed
- **THEN** WebSocket message with type "device_removed" and device_id is broadcast

#### Scenario: WebSocket message format
- **WHEN** broadcasting device event
- **THEN** message is JSON with fields: type, device (object with all device fields)

### Requirement: In-Memory Storage
The system SHALL store devices in memory (not persisted to database).

#### Scenario: Storage on restart
- **WHEN** backend service restarts
- **THEN** device list is empty (host service will re-notify on next detection)

#### Scenario: Concurrent access
- **WHEN** multiple mount notifications arrive simultaneously
- **THEN** device store handles concurrent access safely

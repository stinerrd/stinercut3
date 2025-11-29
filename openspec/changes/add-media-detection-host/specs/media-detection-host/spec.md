## ADDED Requirements

### Requirement: Device Detection
The system SHALL detect removable media connection and disconnection events.

#### Scenario: USB device connected
- **WHEN** a USB storage device is connected to the host
- **THEN** the service detects the block device add event via pyudev

#### Scenario: USB device removed
- **WHEN** a USB storage device is disconnected from the host
- **THEN** the service detects the block device remove event

#### Scenario: Partition filtering
- **WHEN** block device event is received
- **THEN** only partition-type devices are processed (not whole disks)

#### Scenario: Event debouncing
- **WHEN** multiple partition events occur rapidly (USB 3.0 enumeration)
- **THEN** the service waits 2 seconds before processing to avoid duplicates

### Requirement: Mount Point Resolution
The system SHALL resolve mount points for detected devices.

#### Scenario: Device mounted
- **WHEN** partition device is detected
- **THEN** the service looks up mount point from /proc/mounts

#### Scenario: Delayed mount
- **WHEN** mount point is not immediately available
- **THEN** the service retries up to 6 times with 0.5s intervals

#### Scenario: Unmounted device
- **WHEN** device has no mount point after retries
- **THEN** the service logs warning and skips the device

### Requirement: Backend Notification
The system SHALL notify the backend API of mount events.

#### Scenario: Device mounted notification
- **WHEN** device mount point is resolved
- **THEN** POST /api/devices/mount is called with device_node and mount_path

#### Scenario: Device unmounted notification
- **WHEN** device is removed
- **THEN** POST /api/devices/unmount is called with device_node

#### Scenario: API unavailable
- **WHEN** backend API is not reachable
- **THEN** the service logs error and continues monitoring

#### Scenario: API request format
- **WHEN** sending mount notification
- **THEN** JSON body contains: device_node (e.g., /dev/sdb1), mount_path (e.g., /media/user/GOPRO)

### Requirement: Systemd Integration
The system SHALL run as a systemd service.

#### Scenario: Service start
- **WHEN** `systemctl start stinercut-detector` is executed
- **THEN** the detector daemon starts monitoring devices

#### Scenario: Service stop
- **WHEN** `systemctl stop stinercut-detector` is executed
- **THEN** the detector daemon stops gracefully

#### Scenario: Auto-restart
- **WHEN** detector process crashes unexpectedly
- **THEN** systemd restarts the service automatically

#### Scenario: Boot startup
- **WHEN** system boots with service enabled
- **THEN** detector starts automatically after network is available

### Requirement: Configuration
The system SHALL support configuration via config file.

#### Scenario: API URL configuration
- **WHEN** service starts
- **THEN** backend API URL is read from config.ini

#### Scenario: Log configuration
- **WHEN** service starts
- **THEN** log file path and level are read from config.ini

### Requirement: Logging
The system SHALL log device events and errors.

#### Scenario: Device detection logged
- **WHEN** device is detected
- **THEN** event is logged with device node and action

#### Scenario: API errors logged
- **WHEN** API call fails
- **THEN** error details are logged

#### Scenario: Mount resolution logged
- **WHEN** mount point is resolved
- **THEN** device node and mount path are logged

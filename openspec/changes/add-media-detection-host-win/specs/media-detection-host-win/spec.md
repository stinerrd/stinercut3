## ADDED Requirements

### Requirement: Device Detection
The system SHALL detect removable media connection and disconnection events on Windows 11.

#### Scenario: USB device connected
- **WHEN** a USB storage device is connected to the Windows host
- **THEN** the service detects the volume arrival event via WMI Win32_VolumeChangeEvent (EventType=2)

#### Scenario: USB device removed
- **WHEN** a USB storage device is disconnected from the Windows host
- **THEN** the service detects the volume removal event via WMI Win32_VolumeChangeEvent (EventType=3)

#### Scenario: Removable drive filtering
- **WHEN** volume change event is received
- **THEN** only removable drives (DriveType=2) are processed

#### Scenario: Event debouncing
- **WHEN** multiple volume events occur rapidly (USB 3.0 enumeration)
- **THEN** the service waits 2 seconds before processing to avoid duplicates

### Requirement: Drive Letter Resolution
The system SHALL resolve drive letters for detected devices.

#### Scenario: Drive letter available
- **WHEN** volume arrival event is detected
- **THEN** the service queries Win32_LogicalDisk to get drive letter (e.g., D:, E:)

#### Scenario: Delayed drive letter
- **WHEN** drive letter is not immediately available
- **THEN** the service retries up to 6 times with 0.5s intervals

#### Scenario: No drive letter
- **WHEN** volume has no drive letter after retries
- **THEN** the service logs warning and skips the device

#### Scenario: Volume serial number
- **WHEN** device is detected
- **THEN** the service captures volume serial number as unique device identifier

### Requirement: Backend Notification
The system SHALL notify the backend API of mount events.

#### Scenario: Device mounted notification
- **WHEN** drive letter is resolved
- **THEN** POST /api/devices/mount is called with device_node and mount_path

#### Scenario: Device unmounted notification
- **WHEN** device is removed
- **THEN** POST /api/devices/unmount is called with device_node

#### Scenario: API unavailable
- **WHEN** backend API is not reachable
- **THEN** the service logs error and continues monitoring

#### Scenario: API request format
- **WHEN** sending mount notification
- **THEN** JSON body contains: device_node (volume serial or device ID), mount_path (e.g., D:\)

### Requirement: Windows Service Integration
The system SHALL run as a Windows Service.

#### Scenario: Service start
- **WHEN** service is started via Services.msc or `sc start StinercutDetector`
- **THEN** the detector starts monitoring devices

#### Scenario: Service stop
- **WHEN** service is stopped via Services.msc or `sc stop StinercutDetector`
- **THEN** the detector stops gracefully

#### Scenario: Auto-restart
- **WHEN** detector process crashes unexpectedly
- **THEN** Windows restarts the service automatically (recovery options)

#### Scenario: Boot startup
- **WHEN** system boots with service set to automatic
- **THEN** detector starts automatically

#### Scenario: Service account
- **WHEN** service runs
- **THEN** it runs under Local System or designated service account

### Requirement: Configuration
The system SHALL support configuration via config file.

#### Scenario: API URL configuration
- **WHEN** service starts
- **THEN** backend API URL is read from config.ini

#### Scenario: Log configuration
- **WHEN** service starts
- **THEN** log file path (e.g., %APPDATA%\StinercutDetector\) and level are read from config.ini

### Requirement: Logging
The system SHALL log device events and errors.

#### Scenario: Device detection logged
- **WHEN** device is detected
- **THEN** event is logged with drive letter and event type

#### Scenario: API errors logged
- **WHEN** API call fails
- **THEN** error details are logged

#### Scenario: Drive resolution logged
- **WHEN** drive letter is resolved
- **THEN** device identifier and drive letter are logged

### Requirement: Alternative Tray Application (Optional)
The system MAY run as a system tray application instead of a service.

#### Scenario: Tray icon displayed
- **WHEN** application runs in tray mode
- **THEN** icon is displayed in Windows system tray

#### Scenario: Device notification
- **WHEN** device is detected in tray mode
- **THEN** toast notification is shown to user

#### Scenario: Tray menu
- **WHEN** user right-clicks tray icon
- **THEN** menu with options (Exit, View Log, Scan Now) is displayed

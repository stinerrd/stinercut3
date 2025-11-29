## ADDED Requirements

### Requirement: Device List Display
The system SHALL display connected devices in the UI.

#### Scenario: Show device list
- **WHEN** user views device panel
- **THEN** all connected devices are displayed as cards/rows

#### Scenario: Device information displayed
- **WHEN** device is shown in list
- **THEN** mount path, media type, video count, and photo count are visible

#### Scenario: Empty state
- **WHEN** no devices are connected
- **THEN** message "No devices connected" is displayed

### Requirement: Media Type Display
The system SHALL indicate media type visually.

#### Scenario: Video media indicator
- **WHEN** device has media_type "video"
- **THEN** video icon/badge is displayed

#### Scenario: Photo media indicator
- **WHEN** device has media_type "photo"
- **THEN** photo icon/badge is displayed

#### Scenario: Mixed media indicator
- **WHEN** device has media_type "multi"
- **THEN** mixed media icon/badge is displayed

#### Scenario: No GoPro content indicator
- **WHEN** device has media_type "none" or "empty"
- **THEN** appropriate indicator shows no importable content

### Requirement: Import Action
The system SHALL provide import action for devices.

#### Scenario: Import button displayed
- **WHEN** device is shown in list
- **THEN** "Import" button is visible

#### Scenario: Import button enabled
- **WHEN** device has media_type "video", "photo", or "multi"
- **THEN** Import button is enabled/clickable

#### Scenario: Import button disabled
- **WHEN** device has media_type "none" or "empty"
- **THEN** Import button is disabled/grayed out

#### Scenario: Import action
- **WHEN** user clicks Import button
- **THEN** import workflow is initiated for that device

### Requirement: Real-time Updates via WebSocket
The system SHALL update device list in real-time.

#### Scenario: WebSocket connection
- **WHEN** page loads
- **THEN** WebSocket connection to /ws/devices is established

#### Scenario: Device added event
- **WHEN** "device_added" WebSocket message is received
- **THEN** new device is added to the list without page refresh

#### Scenario: Device removed event
- **WHEN** "device_removed" WebSocket message is received
- **THEN** device is removed from the list without page refresh

#### Scenario: Connection lost
- **WHEN** WebSocket connection is lost
- **THEN** system attempts to reconnect automatically

### Requirement: Initial Data Load
The system SHALL load existing devices on page load.

#### Scenario: Fetch devices on load
- **WHEN** page loads
- **THEN** GET /api/devices is called to fetch current devices

#### Scenario: Populate list
- **WHEN** devices are fetched successfully
- **THEN** device list is populated with all devices

#### Scenario: API error on load
- **WHEN** GET /api/devices fails
- **THEN** error message is displayed to user

### Requirement: Visual Feedback
The system SHALL provide visual feedback for device changes.

#### Scenario: New device highlight
- **WHEN** device is added to list
- **THEN** device card is briefly highlighted/animated

#### Scenario: Device removal animation
- **WHEN** device is removed from list
- **THEN** device card fades out or slides away

### Requirement: Responsive Design
The system SHALL work on various screen sizes.

#### Scenario: Desktop view
- **WHEN** viewport is wide
- **THEN** device list shows full details

#### Scenario: Mobile view
- **WHEN** viewport is narrow
- **THEN** device list adapts to single column layout

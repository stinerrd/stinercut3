## ADDED Requirements

### Requirement: AppController Base Class
The frontend SHALL provide an abstract `AppController` base class that extends Symfony's `AbstractController` and provides methods for injecting page-specific JavaScript files and global JavaScript variables into templates.

#### Scenario: Add page-specific JavaScript file
- **WHEN** a controller calls `$this->addJs('js/my-script.js')`
- **THEN** the script SHALL be loaded via `<script src="{{ asset('js/my-script.js') }}"></script>` in the rendered template

#### Scenario: Add global JavaScript variable
- **WHEN** a controller calls `$this->addJsVar('apiUrl', '/api/endpoint')`
- **THEN** the variable SHALL be available as `window.App.apiUrl` in the browser

#### Scenario: Multiple JavaScript files
- **WHEN** a controller calls `addJs()` multiple times with different paths
- **THEN** all scripts SHALL be loaded in the order they were added

---

### Requirement: Detector Status Dashboard Widget
The dashboard SHALL display a card showing the detector daemon status with a toggle switch to enable/disable device monitoring.

#### Scenario: Display daemon running status
- **WHEN** the dashboard page loads
- **THEN** the widget SHALL show "Running" (green badge) if the detector daemon is responding
- **AND** the widget SHALL show "Offline" (red badge) if the detector daemon is not responding

#### Scenario: Display listener enabled status
- **WHEN** the detector daemon is running with `monitoring_enabled: true`
- **THEN** the toggle switch SHALL be checked and label SHALL show "Enabled"

#### Scenario: Display listener disabled status
- **WHEN** the detector daemon is running with `monitoring_enabled: false`
- **THEN** the toggle switch SHALL be unchecked and label SHALL show "Disabled"

#### Scenario: Toggle disabled when daemon offline
- **WHEN** the detector daemon is not responding
- **THEN** the toggle switch SHALL be disabled

---

### Requirement: Detector Status Auto-Refresh
The detector status widget SHALL automatically refresh the status from the backend API at regular intervals.

#### Scenario: Automatic status polling
- **WHEN** the dashboard page is open
- **THEN** the widget SHALL poll `/api/services/detector/status` every 5 seconds

#### Scenario: Update UI on status change
- **WHEN** the polling detects a status change
- **THEN** the widget SHALL update the badge and toggle state accordingly

---

### Requirement: Detector Monitoring Toggle Control
The user SHALL be able to toggle device monitoring on/off via the dashboard widget.

#### Scenario: Enable monitoring
- **WHEN** the user toggles the switch to ON
- **THEN** the widget SHALL POST to `/api/services/detector/enable`
- **AND** the toggle SHALL remain in its new state on success

#### Scenario: Disable monitoring
- **WHEN** the user toggles the switch to OFF
- **THEN** the widget SHALL POST to `/api/services/detector/disable`
- **AND** the toggle SHALL remain in its new state on success

#### Scenario: Toggle failure feedback
- **WHEN** the toggle API call fails
- **THEN** the toggle SHALL revert to its previous state
- **AND** an error toast notification SHALL be displayed

#### Scenario: Toggle success feedback
- **WHEN** the toggle API call succeeds
- **THEN** a success toast notification SHALL be displayed

## ADDED Requirements

### Requirement: HTTP Control API

The detector service SHALL expose an HTTP control API for remote management.

#### Scenario: Status endpoint returns service state
- **WHEN** GET request sent to `/status`
- **THEN** response contains JSON with `running` boolean, `monitoring_enabled` boolean, and `pending_events` count

#### Scenario: Enable endpoint starts monitoring
- **WHEN** POST request sent to `/control/enable`
- **THEN** service sets `monitoring_enabled` flag to true
- **AND** response returns JSON with `status: "enabled"` and `monitoring_enabled: true`

#### Scenario: Disable endpoint stops monitoring
- **WHEN** POST request sent to `/control/disable`
- **THEN** service sets `monitoring_enabled` flag to false
- **AND** device events are ignored until re-enabled
- **AND** response returns JSON with `status: "disabled"` and `monitoring_enabled: false`

#### Scenario: Restart endpoint triggers clean restart
- **WHEN** POST request sent to `/control/restart`
- **THEN** service performs graceful shutdown
- **AND** systemd restarts the service automatically

### Requirement: Monitoring State

The detector service SHALL support enabling/disabling device monitoring at runtime.

#### Scenario: Monitoring disabled by default
- **WHEN** detector service starts
- **THEN** `monitoring_enabled` is set to false
- **AND** device events are ignored until explicitly enabled

#### Scenario: Device events ignored when disabled
- **WHEN** `monitoring_enabled` is false
- **AND** USB device is inserted or removed
- **THEN** event is logged at debug level
- **AND** no notification is sent to backend

### Requirement: Control API Configuration

The HTTP control API SHALL be configurable via config.ini.

#### Scenario: Control API disabled by default
- **WHEN** `[control]` section not present in config
- **THEN** HTTP control server is not started

#### Scenario: Custom port configuration
- **WHEN** `port` is set in `[control]` section
- **THEN** HTTP server listens on specified port

#### Scenario: API key authentication
- **WHEN** `api_key` is set in `[control]` section
- **AND** request does not include matching `X-API-Key` header
- **THEN** response returns 401 Unauthorized

## ADDED Requirements

### Requirement: Service Control Endpoints

The backend API SHALL provide endpoints to control host services.

#### Scenario: Get detector status
- **WHEN** GET request sent to `/api/services/detector/status`
- **THEN** response contains detector service status from host
- **AND** includes `running` boolean and `monitoring_enabled` boolean

#### Scenario: Detector unreachable
- **WHEN** GET request sent to `/api/services/detector/status`
- **AND** detector HTTP API is not responding
- **THEN** response contains `running: false` and `error` message

#### Scenario: Enable detector monitoring
- **WHEN** POST request sent to `/api/services/detector/enable`
- **THEN** backend forwards enable command to detector HTTP API
- **AND** response contains `monitoring_enabled: true`

#### Scenario: Disable detector monitoring
- **WHEN** POST request sent to `/api/services/detector/disable`
- **THEN** backend forwards disable command to detector HTTP API
- **AND** response contains `monitoring_enabled: false`

#### Scenario: Restart detector service
- **WHEN** POST request sent to `/api/services/detector/restart`
- **THEN** backend forwards restart command to detector HTTP API
- **AND** response confirms restart initiated

### Requirement: Cross-Platform Service Control

The backend service control endpoints SHALL use a platform-agnostic HTTP interface.

#### Scenario: Linux detector control
- **WHEN** backend runs on Linux host
- **THEN** detector URL defaults to `http://host.docker.internal:8001`

#### Scenario: Configurable detector URL
- **WHEN** `DETECTOR_URL` environment variable is set
- **THEN** backend uses configured URL for detector communication

# websocket-hub Specification

## Purpose
TBD - created by archiving change add-websocket-events. Update Purpose after archive.
## Requirements
### Requirement: WebSocket Connection Endpoint
The backend SHALL provide a WebSocket endpoint for frontend clients to connect and receive events.

#### Scenario: Client connects to WebSocket
- **Given** the backend is running
- **When** a browser connects to `wss://api.stinercut.local/ws/events`
- **Then** the connection is accepted
- **And** the client is added to the broadcast list

#### Scenario: Client disconnects
- **Given** a client is connected to the WebSocket
- **When** the client disconnects (close or error)
- **Then** the client is removed from the broadcast list
- **And** no errors are logged for normal disconnects

### Requirement: Event Broadcast
The backend SHALL broadcast events to all connected WebSocket clients.

#### Scenario: Broadcast device mount event
- **Given** multiple clients are connected to the WebSocket
- **When** a device mount event is triggered via HTTP API
- **Then** all connected clients receive the event
- **And** the event contains `type`, `payload`, and `timestamp` fields

#### Scenario: Broadcast with disconnected client
- **Given** a client connection has become stale
- **When** an event is broadcast
- **Then** the stale client is removed from the broadcast list
- **And** other clients still receive the event

### Requirement: Standard Event Format
All WebSocket events SHALL follow a standard JSON format.

#### Scenario: Event structure
- **Given** any event is broadcast
- **Then** the JSON contains:
  - `type` (string): dot-notation event name (e.g., `device.mounted`)
  - `payload` (object): event-specific data
  - `timestamp` (string): ISO 8601 UTC timestamp

### Requirement: Frontend WebSocket Client
The frontend SHALL provide a reusable WebSocket client with event subscription API.

#### Scenario: Subscribe to event type
- **Given** the WebSocket client is loaded
- **When** code calls `window.App.ws.on('device.mounted', handler)`
- **Then** the handler is registered for that event type
- **And** the handler receives `(payload, fullEvent)` when event arrives

#### Scenario: Automatic reconnection
- **Given** the WebSocket connection is lost
- **When** 3 seconds have elapsed
- **Then** the client attempts to reconnect
- **And** reconnection continues until successful

#### Scenario: Unsubscribe from event
- **Given** a handler is registered for an event type
- **When** code calls `window.App.ws.off('device.mounted', handler)`
- **Then** the handler no longer receives events of that type

### Requirement: Device Event Broadcasting
Device mount/unmount events from the detector SHALL be broadcast to WebSocket clients.

#### Scenario: Device mounted broadcast
- **Given** clients are connected to the WebSocket
- **When** the detector sends POST `/api/devices/mount`
- **Then** a `device.mounted` event is broadcast
- **And** the payload contains `device_node`, `mount_path`, and `label`

#### Scenario: Device unmounted broadcast
- **Given** clients are connected to the WebSocket
- **When** the detector sends POST `/api/devices/unmount`
- **Then** a `device.unmounted` event is broadcast
- **And** the payload contains `device_node` and `mount_path`


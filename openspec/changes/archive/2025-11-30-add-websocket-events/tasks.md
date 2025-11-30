## 1. Backend WebSocket Hub

- [x] 1.1 Create `backend/routers/websocket.py`:
  - Define `clients: Set[WebSocket]` for connection tracking
  - Implement `broadcast(event_type: str, payload: dict)` async function
  - Implement `/ws/events` WebSocket endpoint
  - Handle connection accept, message loop, and disconnect cleanup

- [x] 1.2 Update `backend/main.py`:
  - Import websocket router
  - Register router with `app.include_router(websocket.router)`

## 2. Device Event Broadcasting

- [x] 2.1 Create device endpoints in `backend/routers/services.py`:
  - Add `POST /api/devices/mount` endpoint
  - Add `POST /api/devices/unmount` endpoint
  - Import and call `broadcast()` from websocket module
  - Define Pydantic models for request validation

## 3. Frontend WebSocket Client

- [x] 3.1 Create `frontend/public/js/websocket-client.js`:
  - IIFE pattern with 'use strict'
  - Read `window.App.websocketUrl` for WebSocket URL
  - Implement `connect()` function with WebSocket setup
  - Implement `onmessage` handler to dispatch to registered handlers
  - Implement `onclose` handler with 3-second reconnection
  - Expose `window.App.ws.on(type, handler)` for subscriptions
  - Expose `window.App.ws.off(type, handler)` for unsubscriptions
  - Auto-connect on DOMContentLoaded

- [x] 3.2 Update `frontend/templates/base.html.twig`:
  - Add `<script src="{{ asset('js/websocket-client.js') }}"></script>` before page-specific JS

- [x] 3.3 Update `frontend/src/Controller/AppController.php`:
  - Add `websocketUrl` to default JS variables
  - Use environment variable with fallback: `$_ENV['WEBSOCKET_URL'] ?? 'wss://api.stinercut.local/ws/events'`

- [x] 3.4 Update `frontend/.env`:
  - Add `WEBSOCKET_URL=wss://api.stinercut.local/ws/events`

## 4. Update Detector Widget

- [x] 4.1 Update `frontend/public/js/detector-status.js`:
  - Add `window.App.ws.on('detector.status', updateUI)` subscription
  - Keep initial `fetchStatus()` call on load
  - Remove `setInterval(fetchStatus, POLL_INTERVAL)` polling

## 5. Validation

- [x] 5.1 Test WebSocket connection:
  - Verify browser connects to `wss://api.stinercut.local/ws/events`
  - Verify connection survives page idle
  - Verify automatic reconnection after disconnect

- [x] 5.2 Test event broadcasting:
  - Send test POST to `/api/devices/mount`
  - Verify browser receives `device.mounted` event
  - Verify event format includes type, payload, timestamp

- [x] 5.3 Test detector widget:
  - Verify initial status loads correctly
  - Verify status updates via WebSocket (no polling)
  - Verify toggle still works via HTTP API

## 6. Unified WebSocket Hub (Refactor)

- [x] 6.1 Replace two endpoints with single `/ws` hub
- [x] 6.2 Add client_type query param for routing
- [x] 6.3 Implement message format with command, sender, target, data
- [x] 6.4 Add bidirectional communication (frontend can send commands)
- [x] 6.5 Update frontend websocket-client.js with send() method
- [x] 6.6 Update detector to handle incoming commands via WebSocket

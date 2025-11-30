# Change: Add WebSocket Event System

## Why
The frontend needs to receive real-time push events from the host (detector daemon) and backend without polling. Currently the detector status widget polls every 5 seconds, but events like device mount/unmount should be pushed immediately. A general-purpose WebSocket event system enables real-time updates for various event types with different payloads.

## What Changes
- Implement WebSocket hub in backend for client connections
- Create broadcast mechanism for pushing events to all connected clients
- Implement frontend WebSocket client with event subscription API
- Enable host detector to trigger events via backend HTTP API
- Update detector widget to use WebSocket events instead of polling

## Impact
- Affected specs: `websocket-hub` (new capability)
- Affected code:
  - `backend/routers/websocket.py` - WebSocket hub with broadcast
  - `backend/main.py` - Enable WebSocket router
  - `backend/routers/services.py` - Broadcast device events
  - `frontend/public/js/websocket-client.js` - Shared WebSocket client
  - `frontend/templates/base.html.twig` - Include WebSocket client
  - `frontend/src/Controller/AppController.php` - Add WebSocket URL config

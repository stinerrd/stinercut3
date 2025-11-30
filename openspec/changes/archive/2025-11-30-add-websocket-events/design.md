# Design: WebSocket Event System

## Architecture

```
┌─────────────────┐     HTTP POST      ┌─────────────────┐
│  Host Detector  │ ─────────────────> │  Backend API    │
│  (systemd)      │  /api/devices/*    │  (FastAPI)      │
└─────────────────┘                    └────────┬────────┘
                                                │
                                       broadcasts to connected clients
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │  WebSocket Hub  │
                                       │  /ws/events     │
                                       └────────┬────────┘
                                                │
                              wss://api.stinercut.local/ws/events
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │  Frontend JS    │
                                       │  (Browser)      │
                                       └─────────────────┘
```

## Event Format

All events follow a standard JSON format:

```json
{
  "type": "event.name",
  "payload": { ... },
  "timestamp": "2025-11-29T12:00:00Z"
}
```

## Event Types

| Type | Source | Payload |
|------|--------|---------|
| `device.mounted` | Detector via backend | `device_node`, `mount_path`, `label` |
| `device.unmounted` | Detector via backend | `device_node`, `mount_path` |
| `detector.status` | Backend | `running`, `monitoring_enabled` |
| `job.progress` | Backend (future) | `job_id`, `percent`, `step` |
| `job.completed` | Backend (future) | `job_id`, `output_path` |

## Key Decisions

### WebSocket Location: Backend (FastAPI)
- FastAPI has native async WebSocket support
- Backend already has `websockets` package installed
- Single point for all server-to-client communication
- Traefik proxies WebSocket transparently

### Connection Management
- Simple in-memory set of connected clients
- No authentication required (session-based app)
- Automatic reconnection on client side (3-second delay)

### Event Flow: Detector to Frontend
1. Detector daemon detects USB device mount
2. Detector sends HTTP POST to backend `/api/devices/mount`
3. Backend handler stores event and calls `broadcast()`
4. WebSocket hub sends event to all connected clients
5. Frontend client dispatches to registered handlers

### Frontend Client API
```javascript
// Subscribe to events
window.App.ws.on('device.mounted', function(payload) {
    console.log('Device mounted:', payload.mount_path);
});

// Unsubscribe
window.App.ws.off('device.mounted', handler);
```

## Trade-offs

### Polling vs WebSocket for Detector Status
- **Previous**: 5-second polling to detector HTTP API
- **New**: Initial fetch + WebSocket push on changes
- **Benefit**: Immediate updates, reduced network traffic
- **Cost**: Slightly more complex, requires WebSocket connection

### Global vs Per-Page WebSocket
- **Chosen**: Global WebSocket in `base.html.twig`
- **Reason**: Events may be relevant on multiple pages
- **Alternative**: Page-specific connections (more complex)

## Integration with Existing Code

### Backend Services Router
The existing `/api/services/detector/*` endpoints remain for direct API calls.
Device mount/unmount endpoints will additionally broadcast events.

### Frontend Detector Widget
The `detector-status.js` will:
1. Fetch initial status on page load (existing behavior)
2. Subscribe to `detector.status` events for live updates
3. Remove 5-second polling interval

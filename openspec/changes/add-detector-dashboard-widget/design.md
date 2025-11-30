## Context

The frontend needs to display real-time detector daemon status and allow users to toggle device monitoring. The backend API already exists at `/api/services/detector/*` (implemented in `add-detector-control` change). This design follows the skydivelog2 project patterns for consistency.

## Goals / Non-Goals

**Goals:**
- Display detector daemon running status (Running/Offline)
- Show device listener enabled/disabled state
- Allow toggling listener via switch with AJAX
- Auto-refresh status every 5 seconds
- Provide toast notifications for user feedback

**Non-Goals:**
- Authentication/authorization (public dashboard)
- Persistent state storage (status is read from detector)
- WebSocket real-time updates (polling is sufficient for this use case)

## Decisions

### Decision 1: AppController Base Class
**What:** Create an abstract `AppController` that extends Symfony's `AbstractController`, providing:
- `addJs(string $path)` - Add page-specific JS file to be loaded
- `addJsVar(string $key, mixed $value)` - Add global JS variable (`window.App.*`)
- Override `render()` to merge JS config into template parameters

**Why:** This pattern is proven in skydivelog2 and provides a clean way to inject page-specific JavaScript without modifying Webpack configuration or creating ES modules.

**Alternatives considered:**
- Stimulus controllers: Would require additional setup and adds framework complexity
- Inline `<script>` tags: Harder to maintain and test
- ES modules via Webpack Encore: Requires build step for each change

### Decision 2: Vanilla JavaScript with IIFE Pattern
**What:** Use immediately-invoked function expression (IIFE) pattern for page-specific JS in `public/js/`.

**Why:**
- No build step required
- Works with existing AdminLTE + Bootstrap setup
- Consistent with skydivelog2 patterns
- Easy to debug (source matches runtime)

### Decision 3: Polling vs WebSocket
**What:** Use polling (setInterval) every 5 seconds instead of WebSocket.

**Why:**
- Detector status changes infrequently
- Simpler implementation
- No additional infrastructure (Mercure) needed
- Acceptable latency for this use case

### Decision 4: API URL Configuration
**What:** Pass backend API URL via `window.App.backendApiUrl` from controller.

**Why:**
- Avoids hardcoding URLs in JavaScript
- Can be configured per-environment
- Follows skydivelog2 pattern

## Risks / Trade-offs

**Risk:** Polling every 5 seconds may create unnecessary load.
**Mitigation:** 5-second interval is reasonable; can be made configurable later.

**Risk:** JavaScript in `public/js/` is not type-checked.
**Mitigation:** Keep module small and focused; add JSDoc comments for IDE support.

## Migration Plan

No migration needed - this is a new feature addition.

## Open Questions

None - design is straightforward.

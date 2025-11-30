# Change: Add Detector Status Dashboard Widget

## Why

The frontend dashboard needs to display detector daemon status and provide a toggle switch to enable/disable device monitoring. The backend already provides the API endpoints (`/api/services/detector/*`) but the frontend has no UI to consume them. Users need visibility into the detector service state and the ability to control it without command-line access.

## What Changes

- Create `AppController` base class with `addJs()` and `addJsVar()` helpers (following skydivelog2 pattern)
- Update `HomeController` to extend `AppController` and inject page-specific JavaScript
- Add detector status card component to dashboard template
- Create vanilla JavaScript module for status polling and toggle control
- Update `base.html.twig` to support page-specific JS injection

## Impact

- Affected specs: `frontend-dashboard` (new)
- Affected code:
  - `frontend/src/Controller/AppController.php` - New base controller
  - `frontend/src/Controller/HomeController.php` - Extend AppController
  - `frontend/templates/base.html.twig` - Add JS injection blocks
  - `frontend/templates/home/index.html.twig` - Add detector status card
  - `frontend/public/js/detector-status.js` - New JavaScript module

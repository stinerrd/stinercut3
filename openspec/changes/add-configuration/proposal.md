# Change: Add Configuration System

## Why
Users need global settings and per-project configuration options. The original stinercut uses INI files for configuration. The web version needs database-backed settings with UI for easy management.

## What Changes
- Implement Settings model for global configuration
- Store per-project settings in Project.settings_json
- Create settings API endpoints
- Create settings UI page for global defaults
- Create settings form in project page
- Implement all configuration options from original stinercut.ini

## Impact
- Affected specs: `settings` (new capability)
- Affected code:
  - `backend/models/settings.py` - Settings model
  - `backend/routers/settings.py` - Settings API
  - `frontend/src/Controller/SettingsController.php`
  - `frontend/templates/settings/` - Settings views

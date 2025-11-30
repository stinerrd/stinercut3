# Change: Add Configuration System

## Why
Application settings need to be stored in the database and editable via a web UI. Backend and frontend both need access to these settings. The detector service keeps its file-based config.ini (out of scope).

## What Changes
- Create `setting` table in MySQL for key-value configuration storage
- Implement Setting model in both frontend (Eloquent) and backend (SQLAlchemy)
- Frontend: Web controller renders settings page with inline-editable table
- Frontend: API controller handles per-row AJAX updates
- Backend: Reads settings directly from database (no API endpoints needed)
- Add Settings menu item to sidebar navigation
- Support enum/dropdown inputs for settings with predefined options
  - Settings with `options` JSON array render as `<select>` dropdowns instead of text inputs
  - `video.default_codec`: dropdown with options `[h264, h265, vp9, av1]`
  - `video.default_resolution`: dropdown with options `[1280x720, 1920x1080, 2560x1440, 3840x2160]`

## Architecture Pattern (skydivelog2 Fees Page)
- **SettingsController** (extends AppController) - renders view with flat setting list
- **SettingsApiController** - handles per-row AJAX updates via PUT `/api/settings/{key}`
- **Frontend JS** - event delegation for Edit/Save/Cancel buttons, per-row saves
- **Backend** - reads settings directly from DB using `Setting.get(db, key, default)`

## UI Pattern (Inline Editing)
- Table-based display with columns: Setting, Value, Category, Description, Actions
- Per-row Edit button switches to input field (text, number, dropdown, or textarea based on setting type)
- Dropdown inputs for settings with predefined options
- Individual row saves (no batch save button)
- Bootstrap Toast notifications for success/error feedback
- No delete button (settings predefined, managed via migrations)
- No add form (settings added via migrations)

## Impact
- New database table: `setting` with `options` column for enum values
- New frontend files:
  - `frontend/src/Models/Setting.php`
  - `frontend/src/Controller/SettingsController.php`
  - `frontend/src/Controller/Api/SettingsApiController.php`
  - `frontend/public/js/settings-form.js`
  - `frontend/templates/settings/index.html.twig`
  - `frontend/migrations/2025_11_29_100001_add_options_to_setting.php`
- New backend file:
  - `backend/models/setting.py`
- Modified files:
  - `frontend/templates/components/_sidebar.html.twig`

## Out of Scope
- Detector config.ini remains file-based (unchanged)
- Per-project settings (future enhancement)
- User authentication for settings access
- Batch save operations (replaced by per-row saves)
- Delete functionality (settings managed via migrations)
- Add form (settings added via migrations)

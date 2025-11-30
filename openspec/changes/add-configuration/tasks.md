## Phase 1: Database & Models (COMPLETED)

- [x] 1.1 Create migration `frontend/migrations/2025_11_29_100000_create_setting_table.php`
- [x] 1.2 Add seed data for initial settings (video.*, storage.*)
- [x] 1.3 Run migration

## Phase 2: Frontend Model (COMPLETED)

- [x] 2.1 Create `frontend/src/Models/Setting.php` with Eloquent model
- [x] 2.2 Implement `getTypedValue()` method for type casting
- [x] 2.3 Implement static `get(key, default)` helper method

## Phase 3: Frontend Controllers (COMPLETED)

- [x] 3.1 Create `frontend/src/Controller/SettingsController.php`
- [x] 3.2 Create `frontend/src/Controller/Api/SettingsApiController.php`
- [x] 3.3 Implement GET /api/settings - list all settings
- [x] 3.4 Implement PUT /api/settings/{key} - update single setting
- [x] 3.5 Implement PUT /api/settings/batch - update multiple settings

## Phase 4: Frontend Navigation (COMPLETED)

- [x] 4.1 Update `frontend/templates/components/_sidebar.html.twig`
- [x] 4.2 Add Settings menu item with gear icon

## Phase 5: Backend Model (COMPLETED)

- [x] 5.1 Create `backend/models/setting.py` with SQLAlchemy model
- [x] 5.2 Implement `get(db, key, default)` class method
- [x] 5.3 Implement `get_typed_value()` for type casting

## Phase 6: UI Refactoring - Inline Editing (COMPLETED)

- [x] 6.1 Update `frontend/templates/settings/index.html.twig` - replace tab form with inline-editable table
- [x] 6.2 Add table structure: Setting, Value, Category, Description, Actions columns
- [x] 6.3 Add dual-state HTML for each row (view mode / edit mode)
- [x] 6.4 Add data-setting-key attribute to each row
- [x] 6.5 Add data-original attribute to inputs for cancel restore

## Phase 7: JavaScript Refactoring (COMPLETED)

- [x] 7.1 Update `frontend/public/js/settings-form.js` - replace batch save with inline handlers
- [x] 7.2 Implement event delegation for Edit/Save/Cancel buttons
- [x] 7.3 Implement `enterEditMode(row)` - show input, hide badge, swap buttons
- [x] 7.4 Implement `exitEditMode(row)` - restore badge, hide input, swap buttons
- [x] 7.5 Implement `saveSetting(row)` - PUT to /api/settings/{key}, update display
- [x] 7.6 Implement `showToast(message, type)` - Bootstrap Toast pattern
- [x] 7.7 Implement `updateViewDisplay(row, value, type)` - update badge after save

## Phase 8: Controller Update (COMPLETED)

- [x] 8.1 Update `SettingsController.php` - pass flat list instead of grouped

## Phase 9: Verification (COMPLETED)

- [x] 9.1 Test inline edit for string settings
- [x] 9.2 Test inline edit for integer settings
- [x] 9.3 Test inline edit for boolean settings (if any)
- [x] 9.4 Test cancel restores original value
- [x] 9.5 Test toast notifications appear on save
- [x] 9.6 Test backend can still read updated settings

## Phase 10: Enum/Dropdown Support (COMPLETED)

- [x] 10.1 Create migration `frontend/migrations/2025_11_29_100001_add_options_to_setting.php` adding `options` column
- [x] 10.2 Add `getOptions()` method to `frontend/src/Models/Setting.php`
- [x] 10.3 Add `options` to fillable/visible/casts in Setting model
- [x] 10.4 Add `get_options()` method to `backend/models/setting.py`
- [x] 10.5 Add `options` column to backend Setting SQLAlchemy model
- [x] 10.6 Update `frontend/templates/settings/index.html.twig` to render `<select>` when options exist
- [x] 10.7 Populate initial options for `video.default_codec` and `video.default_resolution`
- [x] 10.8 Test dropdown rendering for settings with options
- [x] 10.9 Test dropdown selections save correctly via API

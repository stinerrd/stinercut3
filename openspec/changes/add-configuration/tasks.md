## 1. Backend - Global Settings
- [ ] 1.1 Create `backend/models/settings.py` - Global settings model
- [ ] 1.2 Create `backend/routers/settings.py` - Settings API
- [ ] 1.3 Implement GET /api/settings - Get all global settings
- [ ] 1.4 Implement PUT /api/settings - Update global settings
- [ ] 1.5 Implement default values initialization

## 2. Global Settings Options
- [ ] 2.1 drop_videos_shorter_than (default: 5 seconds)
- [ ] 2.2 transition_enabled (default: true)
- [ ] 2.3 transition_default (default: crossfade)
- [ ] 2.4 transition_duration (default: 1 second)
- [ ] 2.5 watermark_enabled (default: true)
- [ ] 2.6 watermark_default (asset ID)
- [ ] 2.7 watermark_position (default: bottom-right)
- [ ] 2.8 intro_enabled (default: true)
- [ ] 2.9 intro_default (asset ID)
- [ ] 2.10 outro_enabled (default: true)
- [ ] 2.11 outro_default (asset ID)
- [ ] 2.12 audio_enabled (default: true)
- [ ] 2.13 audio_default (asset ID)
- [ ] 2.14 audio_freefall_default (asset ID)
- [ ] 2.15 audio_volume (default: 0.8)
- [ ] 2.16 pax_welcome_enabled (default: true)
- [ ] 2.17 pax_screen_default (asset ID)

## 3. Backend - Project Settings
- [ ] 3.1 Define project settings schema (overrides global)
- [ ] 3.2 Implement settings inheritance (project overrides global)
- [ ] 3.3 Implement GET /api/projects/{id}/settings
- [ ] 3.4 Implement PUT /api/projects/{id}/settings

## 4. Frontend - Global Settings Page
- [ ] 4.1 Create `frontend/src/Controller/SettingsController.php`
- [ ] 4.2 Create `frontend/templates/settings/index.html.twig`
- [ ] 4.3 Create form for each setting category
- [ ] 4.4 Asset selectors for default assets
- [ ] 4.5 Save button with validation

## 5. Frontend - Project Settings
- [ ] 5.1 Add settings panel to project page
- [ ] 5.2 Show inherited values from global settings
- [ ] 5.3 Allow override per setting
- [ ] 5.4 "Reset to default" button per setting

## 6. Verification
- [ ] 6.1 Test global settings CRUD
- [ ] 6.2 Test project settings override
- [ ] 6.3 Test settings inheritance
- [ ] 6.4 Test UI for all setting types

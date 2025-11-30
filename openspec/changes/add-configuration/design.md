# Design: Configuration System

## Architecture

```
┌─────────────────┐     GET /settings      ┌──────────────────────┐
│                 │ ───────────────────────▶ SettingsController   │
│    Browser      │                         │ (renders HTML only)  │
│                 │ ◀─────────────────────── └──────────────────────┘
│                 │        HTML page
│                 │
│                 │   PUT /api/settings/{key} ┌──────────────────────┐
│   (JS fetch)    │ ───────────────────────▶ SettingsApiController │
│                 │                         │ (per-row JSON)       │
│                 │ ◀─────────────────────── └──────────────────────┘
└─────────────────┘     JSON response

┌─────────────────┐                         ┌──────────────────────┐
│    Backend      │ ─── direct DB query ───▶│   MySQL setting      │
│  (FastAPI)      │                         │      table           │
└─────────────────┘                         └──────────────────────┘
```

## Database Schema

```sql
CREATE TABLE setting (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(255) NOT NULL UNIQUE,
    value TEXT NULL,
    type ENUM('string', 'integer', 'boolean', 'json') DEFAULT 'string',
    options TEXT NULL,
    category VARCHAR(100) NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

The `options` column stores a JSON array of allowed values. When populated, the UI renders a `<select>` dropdown instead of a text input.

## Initial Settings

| Key | Type | Category | Default | Options | Label |
|-----|------|----------|---------|---------|-------|
| `video.default_codec` | string | video | h264 | `["h264", "h265", "vp9", "av1"]` | Default Codec |
| `video.default_resolution` | string | video | 1920x1080 | `["1280x720", "1920x1080", "2560x1440", "3840x2160"]` | Default Resolution |
| `video.default_fps` | integer | video | 30 | — | Default Frame Rate |
| `video.default_bitrate` | string | video | 8M | — | Default Bitrate |
| `storage.upload_path` | string | storage | /shared-videos/uploads | — | Upload Path |
| `storage.output_path` | string | storage | /shared-videos/output | — | Output Path |
| `storage.temp_path` | string | storage | /shared-videos/temp | — | Temp Path |
| `storage.max_upload_size` | integer | storage | 5368709120 | — | Max Upload Size (bytes) |

## UI Layout (Inline Editable Table)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Settings                                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│ Setting              │ Value          │ Category │ Description    │ Actions │
├──────────────────────┼────────────────┼──────────┼────────────────┼─────────┤
│ Default Codec        │ [h264]         │ video    │ Default video… │ [✎]     │  ← View mode
│ Default Resolution   │ [1920x1080___] │ video    │ Default output │ [💾][✕] │  ← Edit mode
│ Default Frame Rate   │ [30]           │ video    │ Default frames │ [✎]     │
│ ...                  │                │          │                │         │
└──────────────────────┴────────────────┴──────────┴────────────────┴─────────┘
```

## Row States

**View Mode (default):**
- Value shown as badge
- Edit button visible

**Edit Mode:**
- Value shown as:
  - `<select>` dropdown if setting has predefined `options`
  - `<input type="number">` if type is `integer`
  - `<select>` with true/false options if type is `boolean`
  - `<textarea>` if type is `json`
  - `<input type="text">` otherwise (default)
- Save/Cancel buttons visible
- Input/select focused

## HTML Structure

```html
<tr data-setting-key="video.default_codec">
    <td>Default Codec</td>
    <td>
        <span class="setting-view"><span class="badge bg-primary">h264</span></span>
        <span class="setting-edit" style="display: none;">
            <input type="text" class="form-control form-control-sm setting-input"
                   value="h264" data-original="h264">
        </span>
    </td>
    <td><span class="badge bg-info">video</span></td>
    <td class="text-muted">Default video codec for output files</td>
    <td>
        <div class="btn-group setting-view-buttons">
            <button class="btn btn-sm btn-primary btn-edit"><i class="bi bi-pencil"></i></button>
        </div>
        <div class="btn-group setting-edit-buttons" style="display: none;">
            <button class="btn btn-sm btn-success btn-save"><i class="bi bi-check-lg"></i></button>
            <button class="btn btn-sm btn-secondary btn-cancel"><i class="bi bi-x-lg"></i></button>
        </div>
    </td>
</tr>
```

## JavaScript Pattern (Event Delegation)

```javascript
(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', init);

    function init() {
        document.addEventListener('click', function(e) {
            const editBtn = e.target.closest('.btn-edit');
            const saveBtn = e.target.closest('.btn-save');
            const cancelBtn = e.target.closest('.btn-cancel');

            if (editBtn) enterEditMode(editBtn.closest('tr'));
            if (saveBtn) saveSetting(saveBtn.closest('tr'));
            if (cancelBtn) exitEditMode(cancelBtn.closest('tr'));
        });
    }

    function enterEditMode(row) {
        row.querySelector('.setting-view').style.display = 'none';
        row.querySelector('.setting-edit').style.display = '';
        row.querySelector('.setting-view-buttons').style.display = 'none';
        row.querySelector('.setting-edit-buttons').style.display = '';

        const input = row.querySelector('.setting-input');
        input.focus();
        if (input.select) input.select();
    }

    function exitEditMode(row) {
        row.querySelector('.setting-view').style.display = '';
        row.querySelector('.setting-edit').style.display = 'none';
        row.querySelector('.setting-view-buttons').style.display = '';
        row.querySelector('.setting-edit-buttons').style.display = 'none';

        // Reset to original value
        const input = row.querySelector('.setting-input');
        if (input.dataset.original !== undefined) {
            input.value = input.dataset.original;
        }
    }

    function saveSetting(row) {
        const key = row.dataset.settingKey;
        const input = row.querySelector('.setting-input');
        const newValue = input.value;

        fetch('/api/settings/' + encodeURIComponent(key), {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ value: newValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateViewDisplay(row, newValue, data.data.type);
                input.dataset.original = newValue;
                exitEditMode(row);
                showToast('Setting updated successfully', 'success');
            } else {
                showToast(data.error || 'Failed to save', 'danger');
            }
        })
        .catch(error => showToast('Network error', 'danger'));
    }

    function showToast(message, type) {
        // Bootstrap Toast pattern (see detector-status.js)
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }

        const toastEl = document.createElement('div');
        toastEl.className = 'toast align-items-center text-bg-' + type + ' border-0';
        toastEl.innerHTML = '<div class="d-flex"><div class="toast-body">' + message +
            '</div><button class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>';

        container.appendChild(toastEl);
        new bootstrap.Toast(toastEl, { delay: 3000 }).show();
        toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
    }
})();
```

## Controller Pattern

### Web Controller (View Only)
```php
class SettingsController extends AppController
{
    #[Route('/settings', name: 'app_settings')]
    public function index(): Response
    {
        $this->addJs('js/settings-form.js');

        // Flat list ordered by category and label
        $settings = Setting::orderBy('category')->orderBy('label')->get();

        return $this->render('settings/index.html.twig', [
            'settings' => $settings,
        ]);
    }
}
```

### API Controller (Per-Row Updates)
```php
#[Route('/api/settings')]
class SettingsApiController extends AbstractController
{
    #[Route('/{key}', name: 'api_settings_update', methods: ['PUT'])]
    public function update(string $key, Request $request): JsonResponse
    {
        $setting = Setting::where('key', $key)->first();
        if (!$setting) {
            return new JsonResponse(['success' => false, 'error' => 'Not found'], 404);
        }

        $data = json_decode($request->getContent(), true);
        $setting->value = (string) $data['value'];
        $setting->save();

        return new JsonResponse([
            'success' => true,
            'message' => 'Setting updated',
            'data' => $setting->toArray()
        ]);
    }
}
```

## Backend Usage

Backend reads settings directly from database - no API needed:

```python
class Setting(Base):
    @classmethod
    def get(cls, db: Session, key: str, default=None):
        setting = db.query(cls).filter(cls.key == key).first()
        return setting.get_typed_value() if setting else default

# Usage in backend code:
codec = Setting.get(db, "video.default_codec", "h264")
max_size = Setting.get(db, "storage.max_upload_size", 5368709120)
```

## Enum/Dropdown Support

### Template Rendering Logic

```twig
{% set opts = setting.options %}
{% if opts is not empty %}
    {# Dropdown for settings with predefined options #}
    <select class="form-control form-control-sm setting-input"
            data-original="{{ setting.value }}" data-type="{{ setting.type }}">
        {% for opt in opts %}
            <option value="{{ opt }}" {% if setting.value == opt %}selected{% endif %}>{{ opt }}</option>
        {% endfor %}
    </select>
{% elseif setting.type == 'integer' %}
    <input type="number" ...>
{% elseif setting.type == 'boolean' %}
    <select>true/false</select>
{% elseif setting.type == 'json' %}
    <textarea ...>
{% else %}
    <input type="text" ...>
{% endif %}
```

### Setting Model Cast (Eloquent)

```php
protected $casts = [
    "options" => "array",  // Auto-decode JSON to PHP array
    "created_at" => "datetime",
    "updated_at" => "datetime",
];
```

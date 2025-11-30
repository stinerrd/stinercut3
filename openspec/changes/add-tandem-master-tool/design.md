# Design: Tandem Master Management Tool

## Database Schema

```sql
CREATE TABLE tandem_master (
  id BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  image MEDIUMBLOB NULL,
  image_mime VARCHAR(50) NULL,
  active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_active (active)
) ENGINE=InnoDB CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Settings entries:**
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `avatar.max_upload_size` | integer | 5242880 | Max upload size (5MB) |
| `avatar.width` | integer | 150 | Resize width in pixels |
| `avatar.height` | integer | 150 | Resize height in pixels |

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tandem-masters` | List all (optional `?active=true` filter) |
| GET | `/api/tandem-masters/{id}/image` | Return image binary with Content-Type |
| POST | `/api/tandem-masters` | Create new (JSON: name, active) |
| PUT | `/api/tandem-masters/{id}` | Update (JSON: name, active) |
| DELETE | `/api/tandem-masters/{id}` | Delete tandem master |
| POST | `/api/tandem-masters/{id}/image` | Upload avatar (multipart/form-data) |

## Image Upload Flow

```
User clicks avatar → File picker (accept="image/*")
    ↓
JavaScript validates file size against setting
    ↓
POST /api/tandem-masters/{id}/image
    ↓
Server validates size and MIME type
    ↓
GD: Resize to 150x150, convert to JPEG
    ↓
Store in image BLOB, set image_mime
    ↓
Return updated JSON, refresh UI
```

## UI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Tandem Masters                                                   │
├─────────────────────────────────────────────────────────────────┤
│ Name: [_______________] [Add Tandem Master]                     │
├─────────────────────────────────────────────────────────────────┤
│ Image          │ Name      │ Active │ Actions                   │
├────────────────┼───────────┼────────┼───────────────────────────┤
│ [avatar]       │ thomas    │ [ ]    │ [🗑]                      │
│ [avatar]       │ vowa      │ [✓]    │ [🗑]                      │
└────────────────┴───────────┴────────┴───────────────────────────┘
```

- Click image → upload new avatar
- Toggle checkbox → auto-save active status
- Delete button → confirmation dialog

## Key Decisions

1. **BLOB storage** - Images stored in database for session-based architecture consistency
2. **GD resizing** - Server-side resize to 150x150 JPEG for consistent display
3. **Settings-driven** - Upload limits configurable via settings table
4. **Auto-save** - Active checkbox saves immediately on change

# Design: Add Workloads Management

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                        │
├─────────────────────────────────────────────────────────────────┤
│  index.html.twig                                                │
│  ├── Collapsible Filter Panel                                   │
│  ├── _table.html.twig (AJAX-replaceable)                        │
│  │   ├── Workload rows                                          │
│  │   └── _pagination.html.twig                                  │
│  ├── Create/Edit Modal                                          │
│  └── Delete Confirmation Modal                                  │
├─────────────────────────────────────────────────────────────────┤
│  JavaScript                                                      │
│  ├── ajax-content-loader.js (utility)                           │
│  └── workload.js (pagination, filters, CRUD)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ AJAX (POST/PUT/DELETE)
┌─────────────────────────────────────────────────────────────────┐
│                    Symfony Controllers                           │
├─────────────────────────────────────────────────────────────────┤
│  WorkloadController                                              │
│  └── /workloads (GET) → renders index.html.twig                 │
├─────────────────────────────────────────────────────────────────┤
│  WorkloadApiController                                           │
│  ├── /api/workloads (POST) → paginated list (HTML/JSON)         │
│  ├── /api/workloads/{id} (GET) → single workload                │
│  ├── /api/workloads/create (POST) → create new                  │
│  ├── /api/workloads/{id} (PUT) → update                         │
│  └── /api/workloads/{id} (DELETE) → delete                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                 │
├─────────────────────────────────────────────────────────────────┤
│  WorkloadService                                                 │
│  ├── getAll(), find(id), getPaginated(page, perPage, filters)   │
│  ├── create(data), update(entity, data), delete(entity)         │
│  └── UUID generation via Symfony\Component\Uid\Uuid::v4()       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Repository Layer                              │
├─────────────────────────────────────────────────────────────────┤
│  WorkloadRepository (extends Eloquent Model)                     │
│  ├── Eloquent queries with filters                              │
│  ├── Pagination calculation (offset, limit, total)              │
│  ├── Model ↔ Entity conversion                                  │
│  └── BelongsTo TandemMaster relationship                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Database (MySQL)                              │
├─────────────────────────────────────────────────────────────────┤
│  workload table                                                  │
│  ├── id, uuid, name, email, phone, tandem_master_id (FK)        │
│  ├── status, desired_date, video, photo, marketing_flag         │
│  └── created_at, updated_at                                     │
│                                                                  │
│  Indexes: tandem_master_id, status, desired_date, video, photo  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

### 1. Status as VARCHAR vs ENUM

**Decision**: Use VARCHAR(50) for status field

**Rationale**:
- Adding new statuses doesn't require database migration
- Status validation happens in PHP via constants
- Easier to maintain and extend
- Trade-off: Slightly less storage efficiency, but negligible

**Implementation**:
```php
// Entity constants
public const STATUS_CREATED = 'created';
public const STATUS_PROCESSING = 'processing';
public const STATUS_DONE = 'done';
public const STATUS_ARCHIVED = 'archived';

public const STATUSES = [
    self::STATUS_CREATED,
    self::STATUS_PROCESSING,
    self::STATUS_DONE,
    self::STATUS_ARCHIVED,
];
```

### 2. UUIDv4 Generation

**Decision**: Generate UUIDs in PHP, not database

**Rationale**:
- MySQL's UUID() generates UUIDv1 (time-based), we want UUIDv4 (random)
- Symfony's Uid component provides robust UUIDv4 generation
- Consistent with application-layer control of identifiers

**Implementation**:
```php
use Symfony\Component\Uid\Uuid;

$workload->setUuid(Uuid::v4()->toRfc4122());
```

### 3. AJAX Pagination Pattern

**Decision**: POST-based pagination with HTML response for AJAX, JSON for API

**Rationale**:
- Follows proven skydivelog2 pattern
- HTML response allows server-side template rendering
- Browser history management via pushState
- Smooth UX without full page reloads

**Flow**:
1. User clicks page/filter → JavaScript intercepts
2. POST to /api/workloads with page + filters
3. Server renders _table.html.twig partial
4. JavaScript replaces #workloads_content with response
5. pushState updates URL for back/forward support

### 4. Filter Architecture

**Decision**: Collapsible filter panel with Apply/Reset buttons

**Rationale**:
- Keeps UI clean when filters not needed
- Explicit Apply button prevents unexpected behavior
- Reset button returns to default state (today's date)
- All filters combined with AND logic

**Filter Parameters**:
| Parameter | Type | Default |
|-----------|------|---------|
| date | DATE | today |
| status | string | (none) |
| tandem_master_id | int | (none) |
| video | enum | (none) |
| photo | enum | (none) |

### 5. TandemMaster Relationship

**Decision**: Nullable FK with ON DELETE SET NULL

**Rationale**:
- Workloads should persist even if tandem master is deleted
- Historical data preserved for reporting
- NULL indicates "unassigned" state

**Implementation**:
```php
// Migration
$table->foreignId('tandem_master_id')
    ->nullable()
    ->constrained('tandem_master')
    ->nullOnDelete();

// Repository relationship
public function tandemMaster(): BelongsTo
{
    return $this->belongsTo(TandemMasterRepository::class, 'tandem_master_id');
}
```

## File Structure

```
frontend/
├── migrations/
│   └── 2025_12_02_000001_create_workload_table.php
├── src/
│   └── Workload/
│       ├── Entity/
│       │   └── Workload.php
│       ├── Repository/
│       │   └── WorkloadRepository.php
│       ├── Service/
│       │   └── WorkloadService.php
│       └── Controller/
│           ├── WorkloadController.php
│           └── Api/
│               └── WorkloadApiController.php
├── templates/
│   ├── _pagination.html.twig (shared)
│   └── Workload/
│       ├── index.html.twig
│       └── _table.html.twig
└── public/
    └── js/
        ├── ajax-content-loader.js (shared utility)
        └── workload.js
```

## API Response Formats

### Paginated List (HTML for AJAX)
Returns rendered `_table.html.twig` including pagination

### Paginated List (JSON for API)
```json
{
  "success": true,
  "data": {
    "workloads": [
      {
        "id": 1,
        "uuid": "550e8400-e29b-41d4-a716-446655440000",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "tandem_master_id": 5,
        "tandem_master_name": "Mike Smith",
        "status": "created",
        "desired_date": "2025-12-02",
        "video": "yes",
        "photo": "maybe",
        "marketing_flag": false,
        "created_at": "2025-12-02T10:30:00Z",
        "updated_at": "2025-12-02T10:30:00Z"
      }
    ],
    "pagination": {
      "currentPage": 1,
      "totalPages": 5,
      "total": 98,
      "perPage": 20
    }
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Name is required"
}
```

## Security Considerations

- Input validation on all API endpoints
- ENUM values validated against allowed options
- SQL injection prevented via Eloquent parameterized queries
- XSS prevented via Twig auto-escaping
- CSRF protection via Symfony's built-in mechanisms

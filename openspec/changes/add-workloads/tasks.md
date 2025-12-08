# Tasks: Add Workloads Management

## Phase 1: Database & Domain Layer

1. [x] Create migration `2025_12_02_000001_create_workload_table.php`
   - Table: `workload` with all columns (id, uuid, name, email, phone, tandem_master_id, status, desired_date, video, photo, marketing_flag, timestamps)
   - email: VARCHAR(255) nullable
   - phone: VARCHAR(50) nullable
   - Foreign key to tandem_master with ON DELETE SET NULL
   - Indexes on: tandem_master_id, status, desired_date, video, photo
   - Verify: Run migration, check table structure in MySQL

2. [x] Create Entity `src/Workload/Entity/Workload.php`
   - Private properties with types (including email, phone as nullable strings)
   - Constants: STATUS_CREATED, STATUS_PROCESSING, STATUS_DONE, STATUS_ARCHIVED
   - Constants: MEDIA_YES, MEDIA_NO, MEDIA_MAYBE
   - Static arrays: STATUSES, MEDIA_OPTIONS
   - Getters/setters with fluent interface
   - toArray() method
   - Verify: Unit test or manual instantiation test

3. [x] Create Repository `src/Workload/Repository/WorkloadRepository.php`
   - Extend Eloquent Model, set $table, $fillable, $casts
   - BelongsTo relationship to TandemMaster
   - findAll(), findById(), saveEntity(), deleteEntity()
   - findPaginated(int $page, int $perPage, array $filters)
   - modelToEntity() and modelsToEntities() conversion
   - Verify: Test pagination with sample data

4. [x] Create Service `src/Workload/Service/WorkloadService.php`
   - Constructor injection of WorkloadRepository
   - getAll(), find(), create(), update(), delete()
   - getPaginated(int $page, int $perPage, array $filters)
   - UUIDv4 generation in create() using Symfony\Component\Uid\Uuid::v4()
   - Verify: Test service methods via tinker or controller

## Phase 2: API Layer

5. [x] Create API Controller `src/Workload/Controller/Api/WorkloadApiController.php`
   - POST /api/workloads - list (paginated, with filters)
   - GET /api/workloads/{id} - show single
   - POST /api/workloads/create - create new (status always set to "created" by service)
   - PUT /api/workloads/{id} - update existing
   - DELETE /api/workloads/{id} - delete
   - Validation for required fields and enum values
   - HTML response for AJAX, JSON for API calls
   - Verify: Test all endpoints with curl/Postman

## Phase 3: Frontend Templates

6. [x] Create/adapt `templates/_pagination.html.twig`
   - Copy from skydivelog2 if not exists
   - "Showing X-Y of Z" display
   - Page navigation with ellipsis
   - Bootstrap pagination styling
   - Verify: Include in test template

7. [x] Create `src/Workload/templates/_table.html.twig`
   - Table structure with columns: Name, Email, Phone, Tandem Master, Status, Date, Video, Photo, Marketing, Actions
   - Row template for each workload
   - Include pagination component
   - Wrapper div with id="workloads_content" for AJAX replacement
   - Verify: Render with sample data

8. [x] Create `src/Workload/templates/index.html.twig`
   - Extend base AdminLTE layout
   - Collapsible filter card with:
     - Date picker (default: today)
     - Status dropdown
     - Tandem Master dropdown
     - Video/Photo selects
     - Apply/Reset buttons
   - Include _table.html.twig partial
   - Create/Edit modal form with fields: name, email, phone, tandem_master, desired_date, video, photo, marketing_flag (NO status field - set by backend)
   - Delete confirmation modal
   - JavaScript config injection for pagination
   - Verify: Full page render with working filters

## Phase 4: JavaScript & Interactivity

9. [x] Create/adapt `public/js/ajax-content-loader.js`
   - Copy from skydivelog2 if not exists
   - loadContent() function for AJAX requests
   - Support for different response formats
   - Loading indicators
   - Verify: Test basic AJAX call

10. [x] Create `public/js/workload.js`
    - Initialize pagination from window.App config
    - Filter form handling
    - AJAX page loading with loadContent()
    - Browser history management (pushState)
    - Re-initialize handlers after content replacement
    - CRUD modal handling (create, edit, delete) - status field not included in form data
    - Verify: Full AJAX workflow test

## Phase 5: Web Controller & Integration

11. [x] Create Web Controller `src/Workload/Controller/WorkloadController.php`
    - Route: /workloads
    - index() method renders index.html.twig
    - Inject pagination config into window.App
    - Load required JS files
    - Pass initial data (tandem masters list, status options)
    - Verify: Navigate to /workloads, verify full functionality

12. [x] Add sidebar navigation link
    - Add "Workloads" link to sidebar template
    - Set appropriate icon
    - Verify: Link appears and is clickable

## Phase 6: Testing & Polish

13. [x] Test CRUD operations
    - Create workload with all fields
    - Edit workload, verify changes persist
    - Delete workload, verify removal
    - Verify: All operations work correctly

14. [x] Test filtering and pagination
    - Filter by date, status, tandem master
    - Test pagination navigation
    - Test browser back/forward
    - Verify: Filters apply correctly, pagination works

15. [x] Test edge cases
    - Create workload without tandem master
    - Delete tandem master with linked workloads
    - Filter with no results
    - Verify: Graceful handling of all cases

## Dependencies
- Task 1 must complete before Tasks 2-4
- Tasks 2-4 can run in parallel
- Task 5 requires Tasks 3-4
- Tasks 6-8 can start after Task 5
- Tasks 9-10 can start after Task 6
- Task 11 requires Tasks 5, 8, 10
- Tasks 13-15 require Task 11

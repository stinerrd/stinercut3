## Phase 1: Database Migration

- [x] 1.1 Create migration `frontend/migrations/2025_11_30_100000_create_tandem_master_table.php`
- [x] 1.2 Define tandem_master table (id, name, image MEDIUMBLOB, image_mime, active, timestamps)
- [x] 1.3 Add avatar settings to setting table (max_upload_size, width, height)
- [x] 1.4 Run migration

## Phase 2: Eloquent Model

- [x] 2.1 Create `frontend/src/Models/TandemMaster.php`
- [x] 2.2 Define fillable (name, image, image_mime, active)
- [x] 2.3 Add casts (active => boolean)
- [x] 2.4 Add getters/setters for Symfony compatibility
- [x] 2.5 Add static `getActive()` method for dropdown population

## Phase 3: API Controller

- [x] 3.1 Create `frontend/src/Controller/Api/TandemMastersApiController.php`
- [x] 3.2 Implement GET `/api/tandem-masters` - list all with optional active filter
- [x] 3.3 Implement GET `/api/tandem-masters/{id}/image` - return image blob
- [x] 3.4 Implement POST `/api/tandem-masters` - create new
- [x] 3.5 Implement PUT `/api/tandem-masters/{id}` - update name/active
- [x] 3.6 Implement DELETE `/api/tandem-masters/{id}` - delete
- [x] 3.7 Implement POST `/api/tandem-masters/{id}/image` - upload with validation and resize

## Phase 4: Image Processing

- [x] 4.1 Validate file size against `avatar.max_upload_size` setting
- [x] 4.2 Validate MIME type (image/jpeg, image/png, image/gif)
- [x] 4.3 Resize using GD to `avatar.width` x `avatar.height`
- [x] 4.4 Convert to JPEG for consistency
- [x] 4.5 Store binary in image column, MIME in image_mime

## Phase 5: Web Controller

- [x] 5.1 Create `frontend/src/Controller/TandemMastersController.php`
- [x] 5.2 Implement GET `/tandem-masters` route
- [x] 5.3 Inject avatar settings as JS global variables
- [x] 5.4 Add `tandem-masters.js` via `$this->addJs()`

## Phase 6: Template

- [x] 6.1 Create `frontend/templates/tandem_masters/index.html.twig`
- [x] 6.2 Add card with header "Tandem Masters"
- [x] 6.3 Add name input + "Add Tandem Master" button
- [x] 6.4 Add table with Image, Name, Active, Actions columns
- [x] 6.5 Add placeholder image for avatars without images

## Phase 7: JavaScript

- [x] 7.1 Create `frontend/public/js/tandem-masters.js`
- [x] 7.2 Implement add new tandem master (POST)
- [x] 7.3 Implement active checkbox toggle (PUT, auto-save)
- [x] 7.4 Implement delete with confirmation (DELETE)
- [x] 7.5 Implement avatar upload with file size validation
- [x] 7.6 Add toast notifications for success/error

## Phase 8: Navigation

- [x] 8.1 Update `frontend/templates/components/_sidebar.html.twig`
- [x] 8.2 Add "Tandem Masters" menu item with `bi-people` icon

## Phase 9: Testing

- [x] 9.1 Test creating new tandem master
- [ ] 9.2 Test avatar upload and resize
- [x] 9.3 Test active checkbox toggle
- [ ] 9.4 Test delete with confirmation
- [ ] 9.5 Test file size validation (client and server)

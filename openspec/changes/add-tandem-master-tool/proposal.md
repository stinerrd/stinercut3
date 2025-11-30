# Change: Add Tandem Master Management Tool

## Why

The video production workflow requires operator tracking - when an SD card is detected with video content, the system needs to know which tandem master (pilot) and passenger combination captured the footage. Currently, there's no way to manage and select this metadata. A dedicated Tandem Masters management page provides full CRUD operations for operator profiles with avatar support, enabling proper video attribution in the production workflow.

## What Changes

- Add new database table `tandem_master` with columns for name, avatar image/MIME, and active status
- Add settings table entries for avatar upload configuration (size limits, dimensions)
- Create Eloquent model for TandemMaster entity
- Implement web controller and REST API endpoints for CRUD operations
- Build management page UI with image upload and active checkbox filtering
- Add sidebar navigation link to Tandem Masters page
- Implement image validation, resizing, and BLOB storage in database

## Impact

- Affected specs: `tandem-master-management` (new)
- Affected code:
  - `frontend/migrations/` - New migration for tandem_master table
  - `frontend/src/Models/TandemMaster.php` - Eloquent model
  - `frontend/src/Controller/TandemMastersController.php` - Page rendering
  - `frontend/src/Controller/Api/TandemMastersApiController.php` - REST API
  - `frontend/templates/tandem_masters/index.html.twig` - Management page
  - `frontend/public/js/tandem-masters.js` - Client-side logic
  - `frontend/templates/components/_sidebar.html.twig` - Navigation link

Breaking changes: None

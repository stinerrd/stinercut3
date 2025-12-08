# Proposal: Add QR Code Support to Workloads

## Why

Workloads are scheduled tandem skydiving video editing sessions. QR codes provide a portable, scannable reference to workloads, enabling field teams and coordinators to quickly identify sessions without manual entry. This improves operational efficiency and reduces data entry errors.

## What Changes

- **Database Schema**: Add optional `qr` BLOB field to `workloads` table
- **Workload Entity**: Add `qr` property with getter/setter
- **Workload Service**: Generate QR code on workload creation containing "Stinercut: [WORKLOAD_UUID]"
- **UI**: Add action button in workloads table to display QR code in modal popup
- **Migration**: Backward compatible—existing workloads show "No QR available"
- **Dependencies**: Integrate `endroid/qr-code` PHP library for QR generation

## Impact

- **Affected Specs**: `workloads` capability
- **Affected Code**:
  - `frontend/src/Workload/Entity/Workload.php` - Add qr property
  - `frontend/src/Workload/Service/WorkloadService.php` - Add QR generation on create
  - `frontend/src/Workload/Migration/` - Schema migration
  - `frontend/src/Workload/templates/_table.html.twig` - Add QR display button and modal
  - `frontend/src/Workload/Controller/WorkloadController.php` - Add QR display endpoint (if needed)
  - `frontend/composer.json` - Add endroid/qr-code dependency

## Breaking Changes

None. Existing workloads without QR codes are unaffected and display "No QR available". QR field is optional (nullable).

## Key Decisions

1. **Timing**: QR code generated automatically at workload creation time, not on demand (reduces compute overhead)
2. **Format**: Text content is "Stinercut: [WORKLOAD_UUID]" for clear branding and unique identification
3. **Storage**: BLOB stored in database for immediate availability without regeneration
4. **UI Pattern**: Modal popup with Bootstrap for consistency with existing UI (AdminLTE 3)
5. **Backfill**: No backfilling for existing workloads—keeps migration simple and clean

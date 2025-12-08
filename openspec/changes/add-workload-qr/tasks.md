## 1. Database & Entity Layer

- [x] 1.1 Create Eloquent migration to add `qr` BLOB column to `workloads` table (nullable)
- [x] 1.2 Run migration to update schema
- [x] 1.3 Add `$qr` property to Workload entity class
- [x] 1.4 Add `getQr()` getter method to Workload entity
- [x] 1.5 Add `setQr()` setter method to Workload entity

## 2. QR Generation Service

- [x] 2.1 Add `endroid/qr-code` to `composer.json` dependencies
- [x] 2.2 Run `composer install` to install QR code library
- [x] 2.3 Create `QrCodeService` class in `frontend/src/Workload/Service/`
- [x] 2.4 Implement `generateQrCode(string $uuid): string` method returning PNG BLOB
- [ ] 2.5 Write unit tests for QR code generation

## 3. Workload Service Integration

- [x] 3.1 Inject `QrCodeService` into `WorkloadService`
- [x] 3.2 Update `WorkloadService::create()` to generate QR code after UUID is set
- [x] 3.3 Set generated QR code on workload entity before persistence
- [ ] 3.4 Update `WorkloadService` tests to verify QR generation

## 4. Frontend UI

- [x] 4.1 Update `frontend/src/Workload/templates/_table.html.twig` to add "View QR" button column
- [x] 4.2 Implement button styling and state (disabled if no QR available)
- [x] 4.3 Create Bootstrap modal template for QR code display
- [x] 4.4 Add modal handler to JavaScript to display/close QR modal
- [x] 4.5 Update table row to show QR code image in modal via data-url or inline base64

## 5. Optional: API Endpoint

- [ ] 5.1 (Optional) Add `GET /api/workloads/{id}/qr` endpoint if QR needs to be retrieved separately
- [ ] 5.2 (Optional) Return QR code as PNG image with `Content-Type: image/png`

## 6. Testing & Documentation

- [ ] 6.1 Create integration test for workload creation with QR generation
- [ ] 6.2 Test workload display with and without QR codes
- [ ] 6.3 Verify backward compatibility with existing workloads (NULL qr field)
- [ ] 6.4 Manual test: Create workload, verify QR visible in table, scan QR code
- [ ] 6.5 Update developer documentation if needed

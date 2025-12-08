## ADDED Requirements

### Requirement: QR Code Generation on Workload Creation
The system SHALL generate a QR code containing "Stinercut: [WORKLOAD_UUID]" when a new workload is created and store it as a BLOB in the database.

#### Scenario: QR code generated for new workload
- **WHEN** a workload is created via WorkloadService::create()
- **THEN** a QR code is generated with text "Stinercut: [UUID]"
- **AND** the QR code BLOB is stored in the workload's `qr` field
- **AND** the workload is persisted to the database

#### Scenario: QR code persists across sessions
- **WHEN** a workload with a QR code is retrieved from the database
- **THEN** the QR code BLOB is available for display
- **AND** the QR code contains the original UUID

### Requirement: QR Code Display in Workloads Table
The system SHALL display a QR code action button in each workload row that opens a modal showing the QR code image when available.

#### Scenario: View QR code for new workload
- **GIVEN** a workload with a generated QR code
- **WHEN** the user clicks the "View QR" button in the workloads table
- **THEN** a modal popup displays the QR code image
- **AND** the modal can be closed by the user

#### Scenario: No QR available for old workload
- **GIVEN** a workload created before QR code feature (no `qr` field value)
- **WHEN** the user attempts to view the workload row
- **THEN** the "View QR" button is disabled or shows "No QR available"
- **AND** no modal is displayed

### Requirement: Database Schema for QR Code Storage
The system SHALL maintain a nullable `qr` BLOB column in the `workloads` table to store QR code image data.

#### Scenario: QR field nullable for backward compatibility
- **GIVEN** an existing workload created before QR code support
- **WHEN** the workload is loaded from the database
- **THEN** the `qr` field is NULL
- **AND** the workload entity remains valid and functional

#### Scenario: QR field populated for new workloads
- **GIVEN** a newly created workload
- **WHEN** it is persisted to the database
- **THEN** the `qr` field contains a BLOB (PNG image binary data)
- **AND** the field is NOT NULL

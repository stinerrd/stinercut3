# workloads Specification

## Purpose
Manage tandem skydiving workloads with video/photo preferences, marketing consent tracking, and daily scheduling capabilities.

## ADDED Requirements

### Requirement: Workload Model
The system SHALL store workloads with the following attributes: id (auto-increment), uuid (UUIDv4), name, email (nullable), phone (nullable), tandem_master_id (nullable FK), status (VARCHAR), desired_date (DATE), video (ENUM: yes/no/maybe), photo (ENUM: yes/no/maybe), marketing_flag (boolean), created_at, updated_at.

#### Scenario: Create new workload
- **GIVEN** a user creates a workload with name and desired_date
- **WHEN** the workload is saved
- **THEN** the system generates a UUIDv4, sets status to "created", defaults video/photo to "maybe", marketing_flag to false, and sets created_at to current timestamp

#### Scenario: Create workload with contact info
- **GIVEN** a user creates a workload with email and/or phone
- **WHEN** the workload is saved
- **THEN** the system stores the contact information for customer follow-up

#### Scenario: Assign tandem master
- **GIVEN** a workload exists
- **WHEN** a tandem master is assigned
- **THEN** the tandem_master_id is updated to reference the tandem master

#### Scenario: Delete tandem master preserves workloads
- **GIVEN** a workload is linked to a tandem master
- **WHEN** the tandem master is deleted
- **THEN** the workload's tandem_master_id is set to NULL (not cascaded)

### Requirement: Workload Status Management
The system SHALL track workload status using VARCHAR field with predefined constants for flexibility.

#### Scenario: Initial status
- **WHEN** a workload is created
- **THEN** status is set to "created"

#### Scenario: Status transitions
- **GIVEN** valid status values: created, processing, done, archived
- **WHEN** status is updated
- **THEN** the system accepts only valid status values

#### Scenario: Add new status
- **GIVEN** a new status value is needed
- **WHEN** the constant is added to the entity
- **THEN** no database migration is required

### Requirement: Workload Filtering
The system SHALL support filtering workloads by multiple criteria.

#### Scenario: Filter by date
- **GIVEN** a desired_date filter is provided
- **WHEN** workloads are queried
- **THEN** only workloads matching the date are returned

#### Scenario: Filter by status
- **GIVEN** a status filter is provided
- **WHEN** workloads are queried
- **THEN** only workloads matching the status are returned

#### Scenario: Filter by tandem master
- **GIVEN** a tandem_master_id filter is provided
- **WHEN** workloads are queried
- **THEN** only workloads assigned to that tandem master are returned

#### Scenario: Filter by video/photo preference
- **GIVEN** video or photo filter is provided
- **WHEN** workloads are queried
- **THEN** only workloads matching the preference are returned

#### Scenario: Combined filters
- **GIVEN** multiple filters are provided
- **WHEN** workloads are queried
- **THEN** all filter conditions are applied with AND logic

### Requirement: Workload Pagination
The system SHALL support paginated queries with metadata.

#### Scenario: Paginated query
- **GIVEN** page number and items per page
- **WHEN** workloads are queried
- **THEN** the system returns workloads for that page with pagination metadata (currentPage, totalPages, total, perPage)

#### Scenario: Default pagination
- **WHEN** no pagination parameters are provided
- **THEN** the system defaults to page 1 with 20 items per page

#### Scenario: Empty results
- **GIVEN** filters that match no workloads
- **WHEN** workloads are queried
- **THEN** the system returns empty results with totalPages=0 and total=0

### Requirement: Workload API Endpoints
The system SHALL provide REST API endpoints for workload management.

#### Scenario: List workloads (paginated)
- **WHEN** POST /api/workloads is called with filters and page
- **THEN** the system returns paginated workloads as HTML (for AJAX) or JSON (based on Accept header)

#### Scenario: Get single workload
- **WHEN** GET /api/workloads/{id} is called
- **THEN** the system returns the workload details as JSON

#### Scenario: Create workload
- **WHEN** POST /api/workloads/create is called with valid data
- **THEN** the system creates the workload and returns 201 with workload data

#### Scenario: Update workload
- **WHEN** PUT /api/workloads/{id} is called with valid data
- **THEN** the system updates the workload and returns 200 with updated data

#### Scenario: Delete workload
- **WHEN** DELETE /api/workloads/{id} is called
- **THEN** the system deletes the workload and returns 200 with success message

#### Scenario: Validation error
- **WHEN** create/update is called with invalid data
- **THEN** the system returns 400 with error details

### Requirement: Workload UI
The system SHALL provide AdminLTE-based UI for workload management.

#### Scenario: Workload list page
- **WHEN** user navigates to /workloads
- **THEN** the system displays workloads in a table with pagination
- **AND** shows collapsible filter panel above the table
- **AND** defaults date filter to today

#### Scenario: Collapsible filter panel
- **WHEN** filter panel is rendered
- **THEN** it displays date picker, status dropdown, tandem master dropdown, video/photo filters
- **AND** provides Apply and Reset buttons
- **AND** can be collapsed/expanded

#### Scenario: AJAX pagination
- **WHEN** user clicks pagination link or applies filters
- **THEN** the system loads results via AJAX without full page reload
- **AND** updates browser history for back/forward navigation

#### Scenario: Create workload modal
- **WHEN** user clicks "Add Workload" button
- **THEN** a modal form displays with all workload fields

#### Scenario: Edit workload modal
- **WHEN** user clicks edit button on a workload row
- **THEN** a modal form displays pre-filled with workload data

#### Scenario: Delete confirmation
- **WHEN** user clicks delete button on a workload row
- **THEN** a confirmation dialog appears before deletion

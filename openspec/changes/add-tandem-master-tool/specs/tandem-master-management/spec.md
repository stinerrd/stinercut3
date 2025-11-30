## ADDED Requirements

### Requirement: Tandem Master Data Storage
The system SHALL store tandem master profiles with name, avatar image, MIME type, and active status in the database.

#### Scenario: Create new tandem master
- **WHEN** a user provides a tandem master name
- **THEN** the system SHALL create a new record in `tandem_master` table with active=true

#### Scenario: Store avatar as BLOB
- **WHEN** a user uploads an avatar image
- **THEN** the system SHALL store the resized image as MEDIUMBLOB in `image` column and MIME type in `image_mime`

### Requirement: Avatar Image Validation and Resizing
The system SHALL validate uploaded images and resize to consistent dimensions.

#### Scenario: Validate file size on server
- **WHEN** an image upload request is received
- **THEN** the system SHALL reject images exceeding `avatar.max_upload_size` setting with HTTP 413

#### Scenario: Resize avatar
- **WHEN** an image passes validation
- **THEN** the system SHALL resize to `avatar.width` x `avatar.height` pixels using GD library

#### Scenario: Client-side validation
- **WHEN** a user selects an image file
- **THEN** the browser SHALL validate file size before upload

### Requirement: Management Page CRUD Interface
The system SHALL provide a web page at `/tandem-masters` for managing tandem master profiles.

#### Scenario: Display all tandem masters
- **WHEN** user navigates to `/tandem-masters`
- **THEN** the system SHALL display a table with Image, Name, Active, Actions columns

#### Scenario: Add new tandem master
- **WHEN** user enters a name and clicks "Add Tandem Master"
- **THEN** the system SHALL create the record and add row to table

#### Scenario: Upload avatar by clicking image
- **WHEN** user clicks on an avatar image
- **THEN** a file picker SHALL open and upload to `/api/tandem-masters/{id}/image`

#### Scenario: Toggle active status
- **WHEN** user clicks the Active checkbox
- **THEN** the system SHALL immediately PUT to update and persist the change

#### Scenario: Delete tandem master
- **WHEN** user clicks delete and confirms
- **THEN** the system SHALL DELETE and remove row from table

### Requirement: REST API Endpoints
The system SHALL provide REST API endpoints for tandem master management.

#### Scenario: List tandem masters
- **WHEN** GET `/api/tandem-masters` is called
- **THEN** return HTTP 200 with JSON array (supports `?active=true` filter)

#### Scenario: Get avatar image
- **WHEN** GET `/api/tandem-masters/{id}/image` is called
- **THEN** return HTTP 200 with binary image data and proper Content-Type

#### Scenario: Create via API
- **WHEN** POST `/api/tandem-masters` with JSON body
- **THEN** return HTTP 201 with created tandem master

#### Scenario: Update via API
- **WHEN** PUT `/api/tandem-masters/{id}` with JSON body
- **THEN** return HTTP 200 with updated tandem master

#### Scenario: Delete via API
- **WHEN** DELETE `/api/tandem-masters/{id}` is called
- **THEN** return HTTP 204 No Content

### Requirement: Active Status Filtering
The system SHALL support filtering by active status for production workflows.

#### Scenario: List only active
- **WHEN** GET `/api/tandem-masters?active=true` is called
- **THEN** return only tandem masters with active=true

### Requirement: Navigation Integration
The system SHALL add Tandem Masters link to sidebar navigation.

#### Scenario: Sidebar link
- **WHEN** user views any page
- **THEN** sidebar SHALL contain "Tandem Masters" item linking to `/tandem-masters`

# database Specification

## Purpose
TBD - created by archiving change add-database-foundation. Update Purpose after archive.
## Requirements
### Requirement: Project Model
The system SHALL store projects with the following attributes: id (UUID), name, created_at, updated_at, status (draft/processing/completed/error), and settings as JSON.

#### Scenario: Create new project
- **WHEN** a new project is created
- **THEN** the system assigns a unique UUID, sets created_at to current timestamp, and status to "draft"

#### Scenario: Update project settings
- **WHEN** project settings are modified
- **THEN** the system updates the settings JSON field and sets updated_at to current timestamp

### Requirement: Video Model
The system SHALL store video metadata with: id (UUID), project_id (foreign key), filename, path (relative to /shared-videos/), duration (seconds), width, height, codec, fps, order (integer for sequencing), in_point, out_point.

#### Scenario: Add video to project
- **WHEN** a video is added to a project
- **THEN** the system creates a video record linked to the project with extracted metadata

#### Scenario: Reorder videos
- **WHEN** video order is changed
- **THEN** the system updates the order field for affected videos

### Requirement: Job Model
The system SHALL store rendering jobs with: id (UUID), project_id (foreign key), status (pending/processing/completed/failed), progress (0-100), started_at, completed_at, error_message, output_path.

#### Scenario: Create render job
- **WHEN** a render is requested
- **THEN** the system creates a job with status "pending" and progress 0

#### Scenario: Update job progress
- **WHEN** rendering progresses
- **THEN** the system updates progress percentage and status

#### Scenario: Job completion
- **WHEN** rendering completes successfully
- **THEN** the system sets status to "completed", progress to 100, completed_at to current timestamp, and stores output_path

#### Scenario: Job failure
- **WHEN** rendering fails
- **THEN** the system sets status to "failed" and stores error_message

### Requirement: Asset Model
The system SHALL store reusable assets with: id (UUID), type (intro/outro/watermark/audio/audio_freefall/pax_template), name, path (relative to /shared-videos/), created_at.

#### Scenario: Upload asset
- **WHEN** an asset is uploaded
- **THEN** the system creates an asset record with appropriate type and path

#### Scenario: List assets by type
- **WHEN** assets are queried by type
- **THEN** the system returns all assets matching the specified type

### Requirement: Database Connection
The system SHALL connect to MySQL using connection configuration from environment variables.

#### Scenario: Backend connection
- **WHEN** backend service starts
- **THEN** SQLAlchemy establishes connection pool to MySQL using DATABASE_URL

#### Scenario: Frontend connection
- **WHEN** frontend service starts
- **THEN** Eloquent establishes connection to MySQL using DB_* environment variables

### Requirement: Eloquent Configuration
The system SHALL use wouterj/eloquent-bundle for Eloquent ORM integration in Symfony.

#### Scenario: Database configuration
- **WHEN** frontend application loads
- **THEN** Eloquent reads connection settings from config/packages/eloquent.yaml

#### Scenario: Model registration
- **WHEN** Eloquent models are accessed
- **THEN** models in App\Models namespace are auto-discovered

### Requirement: Model/Entity/Repository Pattern
The system SHALL separate database access (Models) from business logic (Entities) using repositories.

#### Scenario: Model layer
- **WHEN** database operations are needed
- **THEN** Eloquent models in src/Models/ handle all database interactions

#### Scenario: Entity layer
- **WHEN** business logic is applied
- **THEN** domain entities in src/Entity/ contain validation and business rules

#### Scenario: Repository layer
- **WHEN** data is needed by services
- **THEN** repositories in src/Repository/ convert between Models and Entities

### Requirement: Laravel-style Migrations
The system SHALL use Laravel-style migrations for schema management in frontend.

#### Scenario: Create migration
- **WHEN** schema change is needed
- **THEN** migration file is created in migrations/ directory using anonymous class syntax

#### Scenario: Run migrations
- **WHEN** php bin/console eloquent:migrate is executed
- **THEN** pending migrations are applied to database

#### Scenario: Rollback migration
- **WHEN** php bin/console eloquent:migrate:rollback is executed
- **THEN** last batch of migrations is reversed

### Requirement: Cascade Delete
The system SHALL cascade delete related records when a project is deleted.

#### Scenario: Delete project with videos
- **WHEN** a project is deleted
- **THEN** all associated videos and jobs are also deleted


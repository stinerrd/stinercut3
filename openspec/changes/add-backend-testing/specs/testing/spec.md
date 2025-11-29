## ADDED Requirements

### Requirement: Test Framework
The system SHALL use pytest for automated testing.

#### Scenario: Run all tests
- **WHEN** `pytest` is executed
- **THEN** all tests in tests/ directory run

#### Scenario: Run with coverage
- **WHEN** `pytest --cov=.` is executed
- **THEN** code coverage report is generated

#### Scenario: Run specific test file
- **WHEN** `pytest tests/test_models/test_project.py` is executed
- **THEN** only Project model tests run

### Requirement: Async Test Support
The system SHALL support testing async FastAPI endpoints.

#### Scenario: Async test execution
- **WHEN** test function is marked async
- **THEN** pytest-asyncio handles event loop

#### Scenario: TestClient usage
- **WHEN** httpx TestClient is used
- **THEN** FastAPI app can be tested without server

### Requirement: Test Database Isolation
The system SHALL isolate test data using database transactions.

#### Scenario: Transaction rollback
- **WHEN** a test completes
- **THEN** all database changes are rolled back

#### Scenario: No state leakage
- **WHEN** multiple tests run in sequence
- **THEN** each test starts with clean database state

#### Scenario: Separate test database
- **WHEN** tests run with TEST_DATABASE_URL
- **THEN** tests use tandem_db_test, not tandem_db

### Requirement: Model Unit Tests
The system SHALL have unit tests for all SQLAlchemy models.

#### Scenario: Test Project model
- **WHEN** test_project.py runs
- **THEN** tests verify columns, relationships, defaults, UUID generation

#### Scenario: Test Video model
- **WHEN** test_video.py runs
- **THEN** tests verify foreign key to Project, metadata fields, ordering

#### Scenario: Test Job model
- **WHEN** test_job.py runs
- **THEN** tests verify foreign key to Project, status enum, progress tracking

#### Scenario: Test Asset model
- **WHEN** test_asset.py runs
- **THEN** tests verify type enum, path handling

### Requirement: Test Fixtures
The system SHALL provide pytest fixtures for creating test data.

#### Scenario: Database session fixture
- **WHEN** test requests db_session fixture
- **THEN** a transactional database session is provided

#### Scenario: Create test project fixture
- **WHEN** test requests create_project fixture
- **THEN** factory function for creating Projects is provided

#### Scenario: Create test video fixture
- **WHEN** test requests create_video fixture
- **THEN** factory function for creating Videos linked to Project is provided

#### Scenario: TestClient fixture
- **WHEN** test requests client fixture
- **THEN** httpx TestClient for FastAPI app is provided

### Requirement: Relationship Testing
The system SHALL test SQLAlchemy model relationships.

#### Scenario: Project has many Videos
- **WHEN** project.videos is accessed
- **THEN** list of associated Video objects is returned

#### Scenario: Project has many Jobs
- **WHEN** project.jobs is accessed
- **THEN** list of associated Job objects is returned

#### Scenario: Video belongs to Project
- **WHEN** video.project is accessed
- **THEN** the parent Project object is returned

#### Scenario: Cascade delete Videos
- **WHEN** Project is deleted
- **THEN** all associated Videos are deleted

#### Scenario: Cascade delete Jobs
- **WHEN** Project is deleted
- **THEN** all associated Jobs are deleted

### Requirement: API Endpoint Tests
The system SHALL test FastAPI endpoints.

#### Scenario: Root endpoint
- **WHEN** GET / is called
- **THEN** response contains status "ok" and version

#### Scenario: Health check healthy
- **WHEN** GET /api/health is called with database connected
- **THEN** response contains status "healthy", database "connected"

#### Scenario: Health check unhealthy
- **WHEN** GET /api/health is called with database disconnected
- **THEN** response contains status "unhealthy", database "disconnected"

### Requirement: UUID Generation Tests
The system SHALL test UUID generation for models.

#### Scenario: Auto-generate UUID
- **WHEN** model is created without UUID
- **THEN** unique UUID is automatically assigned

#### Scenario: UUID uniqueness
- **WHEN** multiple models are created
- **THEN** each has unique UUID

#### Scenario: Custom UUID
- **WHEN** model is created with specific UUID
- **THEN** the provided UUID is used

### Requirement: Status Enum Tests
The system SHALL test status field enumerations.

#### Scenario: Project status values
- **WHEN** Project status is set
- **THEN** only draft/processing/completed/error are valid

#### Scenario: Job status values
- **WHEN** Job status is set
- **THEN** only pending/processing/completed/failed/cancelled are valid

#### Scenario: Asset type values
- **WHEN** Asset type is set
- **THEN** only intro/outro/watermark/audio/audio_freefall/pax_template are valid

### Requirement: Default Value Tests
The system SHALL test model default values.

#### Scenario: Project default status
- **WHEN** Project is created without status
- **THEN** status defaults to "draft"

#### Scenario: Job default status
- **WHEN** Job is created without status
- **THEN** status defaults to "pending"

#### Scenario: Job default progress
- **WHEN** Job is created without progress
- **THEN** progress defaults to 0

#### Scenario: Video default order
- **WHEN** Video is created without order
- **THEN** order defaults to 0

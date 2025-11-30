## ADDED Requirements

### Requirement: Test Framework
The system SHALL use PHPUnit 11.5 for automated testing.

#### Scenario: Run unit tests
- **WHEN** `./vendor/bin/phpunit --testsuite Unit` is executed
- **THEN** all unit tests run without database connection

#### Scenario: Run functional tests
- **WHEN** `./vendor/bin/phpunit --testsuite Functional` is executed
- **THEN** all functional tests run against test database

#### Scenario: Run all tests
- **WHEN** `./vendor/bin/phpunit` is executed
- **THEN** both Unit and Functional test suites run

### Requirement: Test Database Isolation
The system SHALL isolate test data using database transactions.

#### Scenario: Transaction rollback
- **WHEN** a functional test completes
- **THEN** all database changes are rolled back

#### Scenario: No state leakage
- **WHEN** multiple tests run in sequence
- **THEN** each test starts with clean database state

#### Scenario: Separate test database
- **WHEN** tests run with APP_ENV=test
- **THEN** tests use stinercut_test, not stinercut

### Requirement: Model Unit Tests
The system SHALL have unit tests for all Eloquent models.

#### Scenario: Test Project model
- **WHEN** ProjectTest runs
- **THEN** tests verify fillable, casts, relationships, getters/setters

#### Scenario: Test Video model
- **WHEN** VideoTest runs
- **THEN** tests verify belongsTo Project, metadata fields, ordering

#### Scenario: Test Job model
- **WHEN** JobTest runs
- **THEN** tests verify belongsTo Project, status enum, progress tracking

#### Scenario: Test Asset model
- **WHEN** AssetTest runs
- **THEN** tests verify type enum constants, path handling

### Requirement: Test Fixtures
The system SHALL provide fixture helpers for creating test data.

#### Scenario: Create test project
- **WHEN** DatabaseFixtures::createProject() is called
- **THEN** a Project with valid defaults is created and persisted

#### Scenario: Create test video
- **WHEN** DatabaseFixtures::createVideo($project) is called
- **THEN** a Video linked to the project is created

#### Scenario: Override defaults
- **WHEN** DatabaseFixtures::createProject(['name' => 'Custom']) is called
- **THEN** the project uses the custom name, other fields use defaults

### Requirement: DatabaseTestCase Base Class
The system SHALL provide a base test class for database operations.

#### Scenario: Transaction management
- **WHEN** test extends DatabaseTestCase
- **THEN** setUp() begins transaction, tearDown() rolls back

#### Scenario: Service access
- **WHEN** test calls getService('service.id')
- **THEN** the service is retrieved from Symfony container

#### Scenario: Migration support
- **WHEN** functional tests run for first time
- **THEN** migrations are executed against test database

### Requirement: Test Environment Configuration
The system SHALL configure test environment separately from development.

#### Scenario: Environment file
- **WHEN** APP_ENV=test
- **THEN** .env.test is loaded with test database credentials

#### Scenario: PHPUnit configuration
- **WHEN** phpunit.xml.dist is present
- **THEN** test suites, bootstrap, and environment are configured

### Requirement: Relationship Testing
The system SHALL test Eloquent model relationships.

#### Scenario: Project hasMany Videos
- **WHEN** project->videos is accessed
- **THEN** collection of associated videos is returned

#### Scenario: Project hasMany Jobs
- **WHEN** project->jobs is accessed
- **THEN** collection of associated jobs is returned

#### Scenario: Video belongsTo Project
- **WHEN** video->project is accessed
- **THEN** the parent project is returned

#### Scenario: Job belongsTo Project
- **WHEN** job->project is accessed
- **THEN** the parent project is returned

### Requirement: Type Casting Tests
The system SHALL test Eloquent attribute casting.

#### Scenario: JSON casting
- **WHEN** Project settings is set with array
- **THEN** it is stored as JSON and retrieved as array

#### Scenario: DateTime casting
- **WHEN** created_at is accessed
- **THEN** it returns Carbon/DateTime instance

#### Scenario: Integer casting
- **WHEN** Video width/height are set
- **THEN** they are cast to integers

#### Scenario: Float casting
- **WHEN** Video duration/fps are set
- **THEN** they are cast to floats

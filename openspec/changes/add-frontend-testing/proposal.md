# Change: Add Frontend Unit Testing

## Why
The frontend application has 4 Eloquent models (Project, Video, Job, Asset) with relationships, type casting, and custom accessor methods but no automated testing. Unit tests ensure code correctness, prevent regressions, and enable confident refactoring as the application grows.

## What Changes
- Add PHPUnit 11.5 and testing dependencies to composer.json
- Create phpunit.xml.dist configuration for test environment
- Create test bootstrap and base classes (DatabaseTestCase)
- Create DatabaseFixtures for consistent test data generation
- Create unit tests for all Eloquent models
- Set up test database (tandem_db_test) with transaction-based isolation

## Impact
- Affected specs: `testing` (new capability)
- Affected code:
  - `frontend/composer.json` - Add PHPUnit and testing dependencies
  - `frontend/phpunit.xml.dist` - PHPUnit configuration
  - `frontend/tests/` - New test directory structure
  - `frontend/.env.test` - Test environment variables

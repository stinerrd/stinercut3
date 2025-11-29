# Change: Add Backend Unit Testing

## Why
The backend has 4 SQLAlchemy models (Project, Video, Job, Asset), database configuration, and FastAPI endpoints but no automated testing. Unit tests ensure code correctness, prevent regressions, and enable confident refactoring as video processing features are added.

## What Changes
- Add pytest and testing dependencies to requirements.txt
- Create pytest.ini configuration for test environment
- Create conftest.py with database fixtures and test client
- Create test database (tandem_db_test) with transaction isolation
- Create unit tests for all SQLAlchemy models
- Create API endpoint tests for health checks
- Set up test fixtures for consistent test data generation

## Impact
- Affected specs: `testing` (new capability)
- Affected code:
  - `backend/requirements.txt` - Add pytest, httpx, pytest-asyncio
  - `backend/pytest.ini` - Pytest configuration
  - `backend/tests/` - New test directory structure
  - `backend/conftest.py` - Shared fixtures

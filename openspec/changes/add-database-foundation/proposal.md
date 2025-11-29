# Change: Add Database Foundation

## Why
The application requires persistent storage for projects, videos, jobs, and assets. Both frontend (Symfony/Eloquent) and backend (FastAPI/SQLAlchemy) need database models to manage video editing workflows.

## What Changes
- Create SQLAlchemy models for Backend (Python): Project, Video, Job, Asset
- Create Eloquent models for Frontend (PHP): Project, Video, Job, Asset
- Create domain entities and repositories following Model/Entity/Repository pattern
- Configure MySQL database connections for both services
- Set up Alembic migrations for backend schema management
- Set up Laravel-style migrations for frontend schema management

## Impact
- Affected specs: `database` (new capability)
- Affected code:
  - `backend/models/` - New SQLAlchemy models
  - `backend/database.py` - Database connection setup
  - `frontend/src/Models/` - New Eloquent models (database layer)
  - `frontend/src/Entity/` - Domain entities (business logic)
  - `frontend/src/Repository/` - Model ↔ Entity conversion
  - `frontend/config/packages/eloquent.yaml` - Database configuration
  - `frontend/migrations/` - Laravel-style migrations

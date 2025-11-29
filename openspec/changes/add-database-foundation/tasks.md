## 1. Backend Database Setup
- [x] 1.1 Create `backend/database.py` with SQLAlchemy engine and session factory
- [x] 1.2 Create `backend/models/__init__.py` with Base model class
- [x] 1.3 Create `backend/models/project.py` - Project model
- [x] 1.4 Create `backend/models/video.py` - Video model
- [x] 1.5 Create `backend/models/job.py` - Job model
- [x] 1.6 Create `backend/models/asset.py` - Asset model
- [x] 1.7 Update `backend/main.py` to initialize database on startup

## 2. Frontend Eloquent Setup
- [x] 2.1 Install Eloquent bundle: `composer require wouterj/eloquent-bundle`
- [x] 2.2 Create `frontend/config/packages/eloquent.yaml` with database configuration
- [x] 2.3 Configure DB_* environment variables in `.env`

## 3. Frontend Eloquent Models
- [x] 3.1 Create `frontend/src/Models/Project.php` - Eloquent model with fillable, casts, relationships
- [x] 3.2 Create `frontend/src/Models/Video.php` - Eloquent model with belongsTo Project
- [x] 3.3 Create `frontend/src/Models/Job.php` - Eloquent model with belongsTo Project
- [x] 3.4 Create `frontend/src/Models/Asset.php` - Eloquent model for reusable assets

## 4. Frontend Domain Entities
- [ ] 4.1 Create `frontend/src/Entity/Project.php` - Domain entity with business logic
- [ ] 4.2 Create `frontend/src/Entity/Video.php` - Domain entity
- [ ] 4.3 Create `frontend/src/Entity/Job.php` - Domain entity
- [ ] 4.4 Create `frontend/src/Entity/Asset.php` - Domain entity

## 5. Frontend Repositories
- [ ] 5.1 Create `frontend/src/Repository/ProjectRepository.php` - Model ↔ Entity conversion
- [ ] 5.2 Create `frontend/src/Repository/VideoRepository.php` - Model ↔ Entity conversion
- [ ] 5.3 Create `frontend/src/Repository/JobRepository.php` - Model ↔ Entity conversion
- [ ] 5.4 Create `frontend/src/Repository/AssetRepository.php` - Model ↔ Entity conversion

## 6. Frontend Migrations
- [x] 6.1 Create migration for `project` table with uuid, name, status, settings
- [x] 6.2 Create migration for `video` table with project_id FK, metadata fields
- [x] 6.3 Create migration for `job` table with project_id FK, status, progress
- [x] 6.4 Create migration for `asset` table with type, name, path
- [x] 6.5 Run migrations: `php bin/console eloquent:migrate`

## 7. Verification
- [x] 7.1 Verify backend can connect to MySQL
- [x] 7.2 Verify frontend Eloquent can connect to MySQL
- [x] 7.3 Verify tables are created correctly
- [ ] 7.4 Test CRUD operations via Eloquent models

## Notes
- Domain Entities and Repositories (sections 4 & 5) deferred to add when business logic requires separation
- Current implementation uses Eloquent Models directly with PropertyAccessor-compatible getters/setters

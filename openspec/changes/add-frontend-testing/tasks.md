## 1. Testing Dependencies
- [ ] 1.1 Add PHPUnit 11.5 to composer.json require-dev
- [ ] 1.2 Add symfony/browser-kit to require-dev
- [ ] 1.3 Add symfony/css-selector to require-dev
- [ ] 1.4 Run composer update to install dependencies

## 2. PHPUnit Configuration
- [ ] 2.1 Create `phpunit.xml.dist` with test suites (Unit, Functional)
- [ ] 2.2 Configure test database environment variables
- [ ] 2.3 Set APP_ENV=test for test environment
- [ ] 2.4 Configure code coverage source directories

## 3. Test Infrastructure
- [ ] 3.1 Create `tests/bootstrap.php` - Load autoloader and env
- [ ] 3.2 Create `tests/DatabaseTestCase.php` - Base class with transaction rollback
- [ ] 3.3 Create `tests/Fixtures/DatabaseFixtures.php` - Test data factory
- [ ] 3.4 Create `.env.test` with test database credentials

## 4. Test Database Setup
- [ ] 4.1 Create stinercut_test database in MySQL
- [ ] 4.2 Configure test database user permissions
- [ ] 4.3 Verify migrations run against test database

## 5. Model Unit Tests
- [ ] 5.1 Create `tests/Unit/Models/ProjectTest.php`
- [ ] 5.2 Create `tests/Unit/Models/VideoTest.php`
- [ ] 5.3 Create `tests/Unit/Models/JobTest.php`
- [ ] 5.4 Create `tests/Unit/Models/AssetTest.php`

## 6. Model Functional Tests
- [ ] 6.1 Create `tests/Functional/Models/ProjectTest.php` - Database operations
- [ ] 6.2 Create `tests/Functional/Models/VideoTest.php` - Relationships
- [ ] 6.3 Create `tests/Functional/Models/JobTest.php` - Status transitions
- [ ] 6.4 Create `tests/Functional/Models/AssetTest.php` - Type filtering

## 7. Verification
- [ ] 7.1 Run `./vendor/bin/phpunit` and verify all tests pass
- [ ] 7.2 Verify test database isolation (no state leakage)
- [ ] 7.3 Document test running instructions in README

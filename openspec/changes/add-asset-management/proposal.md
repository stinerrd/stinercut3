# Change: Add Asset Management

## Why
Users need to manage reusable assets: intro videos, outro videos, watermark logos, background music, freefall audio tracks, and PAX screen templates. A central asset library allows assets to be uploaded once and used across multiple projects.

## What Changes
- Implement Asset model and API endpoints
- Create asset upload functionality for each type
- Implement asset listing and filtering by type
- Implement asset deletion
- Create asset library UI page
- Support preview/playback of assets

## Impact
- Affected specs: `asset-library` (new capability)
- Affected code:
  - `backend/routers/assets.py` - Asset API endpoints
  - `frontend/src/Controller/AssetController.php`
  - `frontend/templates/asset/` - Asset library views

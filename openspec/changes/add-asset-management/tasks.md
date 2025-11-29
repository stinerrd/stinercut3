## 1. Backend API
- [ ] 1.1 Create `backend/routers/assets.py`
- [ ] 1.2 Implement POST /api/assets - Upload asset
- [ ] 1.3 Implement GET /api/assets - List all assets
- [ ] 1.4 Implement GET /api/assets?type=intro - Filter by type
- [ ] 1.5 Implement GET /api/assets/{id} - Get asset details
- [ ] 1.6 Implement DELETE /api/assets/{id} - Delete asset
- [ ] 1.7 Create `backend/schemas/asset.py` - Pydantic schemas

## 2. Asset Types
- [ ] 2.1 Define asset types: intro, outro, watermark, audio, audio_freefall, pax_template
- [ ] 2.2 Validate file types per asset type
- [ ] 2.3 Store assets in /shared-videos/assets/{type}/
- [ ] 2.4 Generate thumbnails for video assets
- [ ] 2.5 Extract duration for audio/video assets

## 3. Frontend - Asset Library
- [ ] 3.1 Create `frontend/src/Controller/AssetController.php`
- [ ] 3.2 Create `frontend/templates/asset/index.html.twig` - Asset library page
- [ ] 3.3 Create tab navigation by asset type
- [ ] 3.4 Display assets with thumbnails/icons
- [ ] 3.5 Add upload form for each asset type

## 4. Frontend - Asset Preview
- [ ] 4.1 Video preview player for intro/outro assets
- [ ] 4.2 Audio player for music assets
- [ ] 4.3 Image preview for watermark assets
- [ ] 4.4 SVG preview for PAX templates

## 5. Frontend - Asset Selection
- [ ] 5.1 Create reusable asset selector component
- [ ] 5.2 Integrate selector in project settings
- [ ] 5.3 Show selected asset preview in project page

## 6. Verification
- [ ] 6.1 Test upload for each asset type
- [ ] 6.2 Test filtering by type
- [ ] 6.3 Test asset deletion
- [ ] 6.4 Test asset preview/playback
- [ ] 6.5 Test asset selection in project

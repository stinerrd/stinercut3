## ADDED Requirements

### Requirement: Asset Upload
The system SHALL allow upload of reusable assets.

#### Scenario: Upload intro video
- **WHEN** user uploads MP4 file as intro asset
- **THEN** the system stores file in /shared-videos/assets/intro/ and creates asset record

#### Scenario: Upload watermark
- **WHEN** user uploads PNG file as watermark asset
- **THEN** the system stores file and creates asset record with type "watermark"

#### Scenario: Invalid file type
- **WHEN** user uploads TXT file as intro
- **THEN** the system returns error "Invalid file type for intro. Expected: MP4, MOV"

### Requirement: Asset Types
The system SHALL support the following asset types: intro, outro, watermark, audio, audio_freefall, pax_template.

#### Scenario: Intro asset
- **WHEN** asset type is "intro"
- **THEN** the system accepts video files (MP4, MOV, MKV)

#### Scenario: Watermark asset
- **WHEN** asset type is "watermark"
- **THEN** the system accepts image files (PNG, JPG, SVG)

#### Scenario: Audio asset
- **WHEN** asset type is "audio" or "audio_freefall"
- **THEN** the system accepts audio files (MP3, WAV, AAC)

#### Scenario: PAX template asset
- **WHEN** asset type is "pax_template"
- **THEN** the system accepts SVG files

### Requirement: Asset Listing
The system SHALL list assets with filtering by type.

#### Scenario: List all assets
- **WHEN** GET /api/assets is called
- **THEN** the system returns all assets sorted by creation date

#### Scenario: Filter by type
- **WHEN** GET /api/assets?type=intro is called
- **THEN** the system returns only intro assets

### Requirement: Asset Details
The system SHALL provide asset metadata including name, type, path, duration (for video/audio), dimensions (for images).

#### Scenario: Video asset details
- **WHEN** getting intro asset details
- **THEN** response includes name, path, duration, width, height

#### Scenario: Audio asset details
- **WHEN** getting audio asset details
- **THEN** response includes name, path, duration

#### Scenario: Image asset details
- **WHEN** getting watermark asset details
- **THEN** response includes name, path, width, height

### Requirement: Asset Deletion
The system SHALL allow deletion of assets not in use.

#### Scenario: Delete unused asset
- **WHEN** user deletes asset not used by any project
- **THEN** the system deletes file and database record

#### Scenario: Delete used asset
- **WHEN** user attempts to delete asset used by active project
- **THEN** the system returns warning "Asset is in use by X projects"

### Requirement: Asset Thumbnails
The system SHALL generate thumbnails for video assets.

#### Scenario: Generate video thumbnail
- **WHEN** video asset is uploaded
- **THEN** the system extracts frame and saves as thumbnail

#### Scenario: Display thumbnail
- **WHEN** asset list is displayed
- **THEN** video assets show thumbnail preview

### Requirement: Asset Library UI
The system SHALL provide UI for managing assets.

#### Scenario: View asset library
- **WHEN** user navigates to asset library
- **THEN** the UI shows tabs for each asset type with uploaded assets

#### Scenario: Upload form
- **WHEN** user clicks upload on intro tab
- **THEN** the UI shows file upload form accepting video files

### Requirement: Asset Preview
The system SHALL allow preview of assets before use.

#### Scenario: Preview video asset
- **WHEN** user clicks preview on intro asset
- **THEN** video player opens showing the intro

#### Scenario: Preview audio asset
- **WHEN** user clicks preview on audio asset
- **THEN** audio player allows playback of the track

#### Scenario: Preview image asset
- **WHEN** user clicks preview on watermark
- **THEN** image is displayed in modal/lightbox

### Requirement: Asset Selection in Projects
The system SHALL allow selection of assets in project settings.

#### Scenario: Select intro for project
- **WHEN** user opens intro selector in project settings
- **THEN** the UI shows list of uploaded intro assets to choose from

#### Scenario: Change asset selection
- **WHEN** user selects different asset
- **THEN** project configuration updates with new asset ID

### Requirement: Asset Storage Organization
The system SHALL organize asset files by type in storage.

#### Scenario: Storage structure
- **WHEN** assets are uploaded
- **THEN** files are stored in /shared-videos/assets/{type}/{filename}

#### Scenario: Unique filenames
- **WHEN** uploading asset with duplicate name
- **THEN** the system appends timestamp to ensure uniqueness

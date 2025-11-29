## ADDED Requirements

### Requirement: Global Settings Storage
The system SHALL store global configuration settings in the database.

#### Scenario: Save global setting
- **WHEN** admin updates global setting
- **THEN** the system persists setting value in database

#### Scenario: Load global settings
- **WHEN** application starts
- **THEN** the system loads all global settings into memory

### Requirement: Per-Project Settings
The system SHALL allow per-project configuration overrides.

#### Scenario: Override global setting
- **WHEN** user sets project-specific transition_enabled to false
- **THEN** project uses false even if global default is true

#### Scenario: Inherit global setting
- **WHEN** project has no override for a setting
- **THEN** project uses global default value

### Requirement: Settings Inheritance
The system SHALL merge project settings with global defaults.

#### Scenario: Get effective settings
- **WHEN** retrieving project settings
- **THEN** the system returns merged object with project values overriding globals

#### Scenario: Reset to default
- **WHEN** user clicks "Reset to default" on a setting
- **THEN** project override is removed and global value is used

### Requirement: Video Duration Threshold
The system SHALL support minimum video duration setting (default: 5 seconds).

#### Scenario: Configure threshold
- **WHEN** drop_videos_shorter_than is set to 10
- **THEN** videos under 10 seconds are rejected on upload

### Requirement: Default Transition Settings
The system SHALL support default transition configuration.

#### Scenario: Transition defaults
- **WHEN** new project is created
- **THEN** project uses global transition_enabled, transition_default, transition_duration

#### Scenario: Available transition types
- **WHEN** user views transition options
- **THEN** options include: none, crossfade, slide

### Requirement: Default Watermark Settings
The system SHALL support default watermark configuration.

#### Scenario: Watermark defaults
- **WHEN** new project is created
- **THEN** project uses global watermark_enabled, watermark_default, watermark_position

#### Scenario: Position options
- **WHEN** user views position options
- **THEN** options include: top-left, top-right, bottom-left, bottom-right

### Requirement: Default Intro/Outro Settings
The system SHALL support default intro/outro configuration.

#### Scenario: Intro defaults
- **WHEN** new project is created
- **THEN** project uses global intro_enabled, intro_default

#### Scenario: Outro defaults
- **WHEN** new project is created
- **THEN** project uses global outro_enabled, outro_default

### Requirement: Default Audio Settings
The system SHALL support default audio configuration.

#### Scenario: Audio defaults
- **WHEN** new project is created
- **THEN** project uses global audio_enabled, audio_default, audio_freefall_default, audio_volume

#### Scenario: Volume range
- **WHEN** setting audio_volume
- **THEN** value must be between 0.0 and 1.0

### Requirement: Default PAX Settings
The system SHALL support default PAX welcome screen configuration.

#### Scenario: PAX defaults
- **WHEN** new project is created
- **THEN** project uses global pax_welcome_enabled, pax_screen_default

### Requirement: Settings API
The system SHALL provide API for settings management.

#### Scenario: Get global settings
- **WHEN** GET /api/settings is called
- **THEN** the system returns all global settings

#### Scenario: Update global settings
- **WHEN** PUT /api/settings is called with valid data
- **THEN** the system updates settings and returns updated values

#### Scenario: Get project settings
- **WHEN** GET /api/projects/{id}/settings is called
- **THEN** the system returns merged settings for project

#### Scenario: Update project settings
- **WHEN** PUT /api/projects/{id}/settings is called
- **THEN** the system updates project-specific overrides

### Requirement: Settings UI
The system SHALL provide UI for managing settings.

#### Scenario: Global settings page
- **WHEN** user navigates to settings
- **THEN** the UI shows all configurable options organized by category

#### Scenario: Project settings panel
- **WHEN** user views project page
- **THEN** the UI shows settings panel with override options

#### Scenario: Show inherited values
- **WHEN** project has no override for a setting
- **THEN** the UI shows global value with "inherited" indicator

### Requirement: Settings Validation
The system SHALL validate settings values.

#### Scenario: Invalid duration
- **WHEN** user enters negative duration
- **THEN** the system shows validation error

#### Scenario: Invalid volume
- **WHEN** user enters volume > 1.0
- **THEN** the system shows validation error

#### Scenario: Invalid asset reference
- **WHEN** user selects non-existent asset
- **THEN** the system shows validation error

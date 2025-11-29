## ADDED Requirements

### Requirement: Logo Watermark Overlay
The system SHALL overlay a logo watermark on the video.

#### Scenario: Apply watermark
- **WHEN** watermark is enabled and logo asset is selected
- **THEN** logo is overlaid on video throughout playback

#### Scenario: No watermark
- **WHEN** watermark is disabled
- **THEN** video has no logo overlay

### Requirement: Watermark Position
The system SHALL allow configurable watermark position.

#### Scenario: Bottom-right position
- **WHEN** position is "bottom-right"
- **THEN** logo appears in bottom-right corner with 10px padding

#### Scenario: Top-left position
- **WHEN** position is "top-left"
- **THEN** logo appears in top-left corner with 10px padding

#### Scenario: All position options
- **WHEN** user views position options
- **THEN** the UI shows: top-left, top-right, bottom-left, bottom-right

### Requirement: Watermark Transparency
The system SHALL support transparent PNG watermarks.

#### Scenario: Transparent logo
- **WHEN** PNG watermark has alpha channel
- **THEN** logo is overlaid with transparency preserved

#### Scenario: Opacity adjustment
- **WHEN** opacity is set to 50%
- **THEN** watermark appears semi-transparent

### Requirement: Watermark Scaling
The system SHALL scale watermark relative to video dimensions.

#### Scenario: Auto-scale watermark
- **WHEN** watermark is larger than 15% of video width
- **THEN** watermark is scaled down to 15% of video width

#### Scenario: Preserve aspect ratio
- **WHEN** watermark is scaled
- **THEN** aspect ratio is preserved

### Requirement: PAX Welcome Screen
The system SHALL generate personalized welcome screens for passengers.

#### Scenario: Create PAX screen
- **WHEN** PAX name is "John Smith" and template is selected
- **THEN** the system generates welcome video with "John Smith" displayed

#### Scenario: No PAX screen
- **WHEN** PAX welcome is disabled
- **THEN** no welcome screen is added to video

### Requirement: PAX Template System
The system SHALL support SVG templates for PAX screens.

#### Scenario: Load SVG template
- **WHEN** PAX screen is generated
- **THEN** the system loads selected SVG template from assets

#### Scenario: Name substitution
- **WHEN** SVG contains {{name}} placeholder
- **THEN** the system replaces with actual passenger name

### Requirement: PAX Screen Duration
The system SHALL create PAX screen with configurable duration.

#### Scenario: Default duration
- **WHEN** PAX screen is generated with default settings
- **THEN** PAX screen is 5 seconds long

#### Scenario: Custom duration
- **WHEN** PAX screen duration is set to 8 seconds
- **THEN** PAX screen is 8 seconds long

### Requirement: PAX Screen Animation
The system SHALL add fade effects to PAX screen.

#### Scenario: Fade in
- **WHEN** PAX screen starts
- **THEN** content fades in over 1 second

#### Scenario: Fade out
- **WHEN** PAX screen ends
- **THEN** content fades out over 1 second

### Requirement: PAX Screen Insertion
The system SHALL prepend PAX screen to main video.

#### Scenario: Insert PAX screen
- **WHEN** PAX screen is enabled
- **THEN** PAX screen appears before main video content

#### Scenario: Order with intro
- **WHEN** both intro and PAX screen are enabled
- **THEN** order is: intro → PAX screen → main content → outro

### Requirement: Overlay Settings UI
The system SHALL provide UI for watermark and PAX configuration.

#### Scenario: Display watermark settings
- **WHEN** user views overlay settings
- **THEN** the UI shows watermark toggle, asset selector, position, opacity

#### Scenario: Display PAX settings
- **WHEN** user views overlay settings
- **THEN** the UI shows PAX toggle, name input, template selector, duration

#### Scenario: Save overlay settings
- **WHEN** user changes overlay settings
- **THEN** settings are saved to project configuration

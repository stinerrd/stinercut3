## ADDED Requirements

### Requirement: Intro Video Prepending
The system SHALL prepend intro video to main content.

#### Scenario: Add intro
- **WHEN** intro is enabled and intro asset is selected
- **THEN** intro video plays before main content

#### Scenario: No intro
- **WHEN** intro is disabled
- **THEN** video starts with main content

### Requirement: Outro Video Appending
The system SHALL append outro video after main content.

#### Scenario: Add outro
- **WHEN** outro is enabled and outro asset is selected
- **THEN** outro video plays after main content

#### Scenario: No outro
- **WHEN** outro is disabled
- **THEN** video ends with main content

### Requirement: Aspect Ratio Handling
The system SHALL handle intro/outro with different aspect ratios than main content.

#### Scenario: Matching aspect ratio
- **WHEN** intro is same aspect ratio as main video (16:9)
- **THEN** intro is scaled to exact output dimensions

#### Scenario: Different aspect ratio
- **WHEN** intro is 4:3 and main video is 16:9
- **THEN** intro is displayed with blurred background fill

### Requirement: Blur Background Effect
The system SHALL use blurred version of content as background fill for aspect ratio mismatches.

#### Scenario: Create blur background
- **WHEN** intro needs padding
- **THEN** a blurred, scaled copy fills the background

#### Scenario: Overlay content
- **WHEN** blur background is created
- **THEN** original content is centered over the blur

### Requirement: Resolution Scaling
The system SHALL scale intro/outro to match main video resolution.

#### Scenario: Scale up
- **WHEN** intro is 720p and main video is 1080p
- **THEN** intro is scaled up to 1080p

#### Scenario: Scale down
- **WHEN** intro is 4K and main video is 1080p
- **THEN** intro is scaled down to 1080p

### Requirement: Codec Matching
The system SHALL encode intro/outro to match main video codec.

#### Scenario: Re-encode intro
- **WHEN** intro codec differs from main video
- **THEN** intro is re-encoded to match for seamless concatenation

#### Scenario: Copy stream
- **WHEN** intro codec matches main video
- **THEN** intro is concatenated without re-encoding (if parameters match)

### Requirement: Final Concatenation Order
The system SHALL concatenate in order: intro → PAX screen → main → outro.

#### Scenario: Full output
- **WHEN** all components are enabled
- **THEN** output order is: intro, PAX screen, main content (with transitions), outro

#### Scenario: Partial output
- **WHEN** only outro is enabled
- **THEN** output is: main content, outro

### Requirement: Intro/Outro Asset Selection
The system SHALL allow selection from uploaded intro/outro assets.

#### Scenario: Select intro
- **WHEN** user selects intro from asset library
- **THEN** selected intro is used for this project

#### Scenario: Change selection
- **WHEN** user selects different intro
- **THEN** new selection replaces previous

### Requirement: Intro/Outro Settings UI
The system SHALL provide UI for intro/outro configuration.

#### Scenario: Display intro settings
- **WHEN** user views intro/outro settings
- **THEN** the UI shows intro toggle, intro selector, outro toggle, outro selector

#### Scenario: Preview thumbnails
- **WHEN** intro/outro is selected
- **THEN** the UI shows thumbnail preview of selected video

#### Scenario: Save settings
- **WHEN** user changes intro/outro settings
- **THEN** settings are saved to project configuration

### Requirement: Intro/Outro Validation
The system SHALL validate intro/outro files before use.

#### Scenario: Valid video file
- **WHEN** selected asset is valid video
- **THEN** asset is accepted for intro/outro use

#### Scenario: Invalid file
- **WHEN** selected asset cannot be processed
- **THEN** the system shows error "Invalid intro/outro video"

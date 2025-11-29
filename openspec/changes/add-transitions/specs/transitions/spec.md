## ADDED Requirements

### Requirement: Crossfade Transition
The system SHALL generate crossfade transitions between video clips.

#### Scenario: Create crossfade
- **WHEN** crossfade transition is enabled between clip A and clip B
- **THEN** the system creates video segment that blends from last frame of A to first frame of B

#### Scenario: Crossfade duration
- **WHEN** transition duration is 1 second
- **THEN** crossfade video segment is 1 second long

### Requirement: Slide Transition
The system SHALL generate slide (push) transitions between video clips.

#### Scenario: Create slide transition
- **WHEN** slide transition is enabled between clip A and clip B
- **THEN** the system creates video segment where clip B pushes clip A off screen

#### Scenario: Slide direction
- **WHEN** slide transition is applied
- **THEN** new clip pushes from right to left (default direction)

### Requirement: Frame Extraction
The system SHALL extract frames from clips for transition generation.

#### Scenario: Extract last frame
- **WHEN** preparing transition after clip A
- **THEN** the system extracts the last frame of clip A as image

#### Scenario: Extract first frame
- **WHEN** preparing transition before clip B
- **THEN** the system extracts the first frame of clip B as image

### Requirement: Transition Duration
The system SHALL allow configurable transition duration (0.5-2 seconds).

#### Scenario: Set duration
- **WHEN** user sets transition duration to 1.5 seconds
- **THEN** all transitions are 1.5 seconds long

#### Scenario: Invalid duration
- **WHEN** user enters duration < 0.5 or > 2
- **THEN** the system shows validation error

### Requirement: No Transition Option
The system SHALL support direct concatenation without transitions.

#### Scenario: Disable transitions
- **WHEN** transition type is set to "none"
- **THEN** clips are concatenated directly without transition segments

### Requirement: Transition Insertion
The system SHALL insert transitions between all adjacent clips.

#### Scenario: Multiple clips with transitions
- **WHEN** project has clips A, B, C with crossfade enabled
- **THEN** output is: A + transition(A→B) + B + transition(B→C) + C

#### Scenario: Single clip no transition
- **WHEN** project has only one clip
- **THEN** no transitions are generated

### Requirement: Resolution Matching
The system SHALL generate transitions matching source video resolution.

#### Scenario: Match resolution
- **WHEN** source videos are 1920x1080
- **THEN** transition video is also 1920x1080

#### Scenario: Mixed resolutions
- **WHEN** clip A is 1080p and clip B is 720p
- **THEN** transition is generated at output resolution (first clip resolution)

### Requirement: Codec Matching
The system SHALL generate transitions with compatible codec for concatenation.

#### Scenario: Match codec
- **WHEN** source videos use H.264
- **THEN** transition video uses H.264

#### Scenario: Re-encode if needed
- **WHEN** lossless concat not possible
- **THEN** transitions are encoded to match target format

### Requirement: Transition Caching
The system SHALL cache generated transitions for reuse.

#### Scenario: Reuse cached transition
- **WHEN** transition with same parameters already exists
- **THEN** the system uses cached file instead of regenerating

#### Scenario: Invalidate cache
- **WHEN** video or settings change
- **THEN** cached transitions are regenerated

### Requirement: Transition Settings UI
The system SHALL provide UI for configuring transition options.

#### Scenario: Display transition settings
- **WHEN** user views project settings
- **THEN** the UI shows transition type dropdown and duration input

#### Scenario: Save transition settings
- **WHEN** user changes transition settings
- **THEN** settings are saved to project configuration

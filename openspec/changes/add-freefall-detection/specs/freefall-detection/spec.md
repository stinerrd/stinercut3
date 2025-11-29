## ADDED Requirements

### Requirement: Freefall Audio Analysis
The system SHALL analyze video audio to detect freefall phase using frequency analysis.

#### Scenario: Detect freefall in skydiving video
- **WHEN** user triggers freefall detection on video with clear freefall audio
- **THEN** the system returns start_time, end_time, duration, and confidence > 0.7

#### Scenario: No freefall detected
- **WHEN** video does not contain freefall audio signature
- **THEN** the system returns confidence < 0.3 and null timecodes

### Requirement: Audio Bandpass Filtering
The system SHALL extract audio with bandpass filter targeting wind noise frequencies (800-1500 Hz).

#### Scenario: Apply frequency filter
- **WHEN** processing video for freefall detection
- **THEN** the system applies FFmpeg highpass=800 and lowpass=1500 filters

#### Scenario: Generate filtered audio
- **WHEN** filters are applied
- **THEN** the system outputs WAV file with only target frequencies

### Requirement: Waveform Generation
The system SHALL generate waveform data using audiowaveform tool.

#### Scenario: Create waveform JSON
- **WHEN** filtered audio is ready
- **THEN** the system runs audiowaveform to produce JSON with amplitude data

#### Scenario: Handle missing tool
- **WHEN** audiowaveform is not installed
- **THEN** the system returns error "audiowaveform tool not found"

### Requirement: Waveform Smoothing
The system SHALL apply smoothing to waveform data to reduce noise.

#### Scenario: Apply smoothing iterations
- **WHEN** waveform data is loaded
- **THEN** the system applies 10 iterations of box smoothing filter

#### Scenario: Preserve peak characteristics
- **WHEN** smoothing is applied
- **THEN** significant peaks remain detectable above noise floor

### Requirement: Peak Detection
The system SHALL detect continuous high-amplitude segments indicating freefall.

#### Scenario: Calculate noise threshold
- **WHEN** analyzing waveform
- **THEN** the system calculates threshold from average amplitude + standard deviation

#### Scenario: Identify peak segments
- **WHEN** amplitude exceeds threshold continuously for > 20 seconds
- **THEN** the system marks segment as potential freefall

### Requirement: Freefall Duration Validation
The system SHALL validate detected freefall duration is within expected range (25-50 seconds typical).

#### Scenario: Valid freefall duration
- **WHEN** detected segment is 35 seconds
- **THEN** confidence score is high (> 0.8)

#### Scenario: Too short segment
- **WHEN** detected segment is 10 seconds
- **THEN** confidence score is reduced (< 0.5)

#### Scenario: Too long segment
- **WHEN** detected segment is 120 seconds
- **THEN** confidence score is reduced, may indicate false positive

### Requirement: Detection API Endpoint
The system SHALL provide API endpoint to trigger freefall detection.

#### Scenario: Trigger detection
- **WHEN** POST /api/projects/{id}/detect-freefall is called
- **THEN** the system analyzes concatenated video and returns detection results

#### Scenario: Return detection results
- **WHEN** detection completes
- **THEN** the system returns JSON: {start: 45.2, end: 92.8, duration: 47.6, confidence: 0.85}

### Requirement: Manual Time Adjustment
The system SHALL allow users to manually adjust detected freefall times.

#### Scenario: Override detected times
- **WHEN** user enters manual start=50.0 and end=95.0
- **THEN** the system saves manual values and uses them for audio processing

#### Scenario: Clear manual override
- **WHEN** user clicks "Use Detected" after manual override
- **THEN** the system reverts to automatically detected times

### Requirement: Confidence Score Display
The system SHALL display detection confidence to help users assess accuracy.

#### Scenario: High confidence display
- **WHEN** confidence > 0.8
- **THEN** the UI shows green indicator with "High confidence"

#### Scenario: Low confidence display
- **WHEN** confidence < 0.5
- **THEN** the UI shows yellow indicator with "Low confidence - manual review recommended"

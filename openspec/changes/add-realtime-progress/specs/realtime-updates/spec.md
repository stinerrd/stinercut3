## ADDED Requirements

### Requirement: WebSocket Connection
The system SHALL provide WebSocket endpoint for real-time job progress.

#### Scenario: Connect to job WebSocket
- **WHEN** client connects to WS /api/ws/jobs/{job_id}
- **THEN** the system accepts connection and streams progress updates

#### Scenario: Connect to invalid job
- **WHEN** client connects with non-existent job_id
- **THEN** the system closes connection with error message

#### Scenario: Multiple clients
- **WHEN** multiple clients connect to same job
- **THEN** all clients receive same progress updates

### Requirement: Progress Event Streaming
The system SHALL emit progress events during video processing.

#### Scenario: Step start event
- **WHEN** a processing step begins
- **THEN** the system emits {type: "step", step: "concatenating", message: "Joining video clips..."}

#### Scenario: Progress percentage event
- **WHEN** FFmpeg reports progress
- **THEN** the system emits {type: "progress", progress: 45, message: "Processing: 45%"}

#### Scenario: Completion event
- **WHEN** processing completes successfully
- **THEN** the system emits {type: "completed", output_path: "output/project_123.mp4"}

#### Scenario: Error event
- **WHEN** processing fails
- **THEN** the system emits {type: "error", message: "FFmpeg error: invalid input"}

### Requirement: Processing Step Names
The system SHALL emit named steps matching the processing pipeline.

#### Scenario: Full pipeline steps
- **WHEN** rendering with all features enabled
- **THEN** the system emits steps in order: "reading_videos", "detecting_freefall", "processing_audio", "creating_transitions", "concatenating", "adding_watermark", "adding_intro_outro", "finalizing"

#### Scenario: Minimal pipeline steps
- **WHEN** rendering with only concatenation
- **THEN** the system emits steps: "reading_videos", "concatenating", "finalizing"

### Requirement: FFmpeg Progress Parsing
The system SHALL parse FFmpeg output for accurate progress percentage.

#### Scenario: Parse time progress
- **WHEN** FFmpeg outputs "time=00:01:30.00" and total duration is 3 minutes
- **THEN** the system calculates progress as 50%

#### Scenario: Handle FFmpeg errors
- **WHEN** FFmpeg outputs error to stderr
- **THEN** the system captures and includes in error event

### Requirement: Progress Bar Display
The system SHALL display visual progress bar in frontend.

#### Scenario: Show progress bar
- **WHEN** render job starts
- **THEN** the frontend displays progress bar at 0%

#### Scenario: Update progress bar
- **WHEN** progress event received with progress: 75
- **THEN** the progress bar animates to 75%

#### Scenario: Complete progress bar
- **WHEN** completion event received
- **THEN** the progress bar shows 100% with success styling

### Requirement: Status Message Display
The system SHALL display current processing step and messages.

#### Scenario: Show step name
- **WHEN** step event received
- **THEN** the frontend displays step name and message

#### Scenario: Show log messages
- **WHEN** multiple events received
- **THEN** the frontend displays scrollable log of messages

### Requirement: Connection Resilience
The system SHALL handle WebSocket disconnections gracefully.

#### Scenario: Reconnect after disconnect
- **WHEN** WebSocket connection drops during processing
- **THEN** the frontend attempts to reconnect and resumes progress display

#### Scenario: Show connection status
- **WHEN** connection is lost
- **THEN** the frontend displays "Reconnecting..." message

### Requirement: Job Completion UI
The system SHALL update UI when job completes.

#### Scenario: Show download button
- **WHEN** completion event received
- **THEN** the frontend displays download button with link to output

#### Scenario: Hide progress on completion
- **WHEN** job completes or fails
- **THEN** the frontend shows final status instead of progress bar

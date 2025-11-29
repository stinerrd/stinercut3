## ADDED Requirements

### Requirement: Render Job Creation
The system SHALL create a render job when user requests video processing.

#### Scenario: Start render
- **WHEN** user clicks "Render" button on project with 3 videos
- **THEN** the system creates a job with status "pending" and returns job ID

#### Scenario: Prevent duplicate render
- **WHEN** user clicks "Render" while another job is processing
- **THEN** the system returns error "A render job is already in progress"

### Requirement: Video Concatenation
The system SHALL concatenate all project videos in order into a single output file.

#### Scenario: Concatenate same codec videos
- **WHEN** all videos use H.264 codec with same parameters
- **THEN** the system uses FFmpeg concat demuxer without re-encoding (fast)

#### Scenario: Concatenate mixed codec videos
- **WHEN** videos have different codecs or parameters
- **THEN** the system re-encodes to unified format (H.264)

#### Scenario: Concatenate with in/out points
- **WHEN** videos have custom in_point and out_point set
- **THEN** the system only includes the trimmed portion of each video

### Requirement: Output Resolution Detection
The system SHALL automatically detect output resolution from source videos.

#### Scenario: Same resolution videos
- **WHEN** all videos are 1920x1080
- **THEN** output is 1920x1080

#### Scenario: Mixed resolution videos
- **WHEN** videos have different resolutions
- **THEN** output uses resolution of first video, others are scaled to match

### Requirement: Job Progress Tracking
The system SHALL track job progress as percentage (0-100).

#### Scenario: Initial progress
- **WHEN** job is created
- **THEN** progress is 0%

#### Scenario: Processing progress
- **WHEN** FFmpeg is running
- **THEN** progress updates based on current time / total duration

#### Scenario: Completion
- **WHEN** processing finishes successfully
- **THEN** progress is 100% and status is "completed"

### Requirement: Job Status Transitions
The system SHALL manage job status: pending -> processing -> completed/failed.

#### Scenario: Start processing
- **WHEN** job is picked up for processing
- **THEN** status changes to "processing" and started_at is set

#### Scenario: Complete successfully
- **WHEN** FFmpeg finishes without error
- **THEN** status changes to "completed" and completed_at is set

#### Scenario: Fail with error
- **WHEN** FFmpeg returns error
- **THEN** status changes to "failed" and error_message is stored

### Requirement: Output File Storage
The system SHALL store rendered videos in /shared-videos/output/{project_id}/.

#### Scenario: Save output
- **WHEN** rendering completes
- **THEN** output file is saved as {project_id}_{timestamp}.mp4

#### Scenario: Store output path
- **WHEN** rendering completes
- **THEN** job.output_path contains relative path to output file

### Requirement: Output Download
The system SHALL allow download of completed render output.

#### Scenario: Download completed video
- **WHEN** user requests download and job is completed
- **THEN** the system returns video file with Content-Disposition header

#### Scenario: Download incomplete job
- **WHEN** user requests download and job is not completed
- **THEN** the system returns error "Render not yet completed"

### Requirement: Temporary File Management
The system SHALL manage temporary files during processing.

#### Scenario: Create temp directory
- **WHEN** processing starts
- **THEN** the system creates /shared-videos/temp/{job_id}/

#### Scenario: Cleanup on success
- **WHEN** processing completes successfully
- **THEN** temporary files are deleted

#### Scenario: Cleanup on failure
- **WHEN** processing fails
- **THEN** temporary files are deleted

### Requirement: FFmpeg Error Handling
The system SHALL capture and report FFmpeg errors.

#### Scenario: Invalid input file
- **WHEN** FFmpeg cannot read input file
- **THEN** job fails with error message from FFmpeg stderr

#### Scenario: Disk full
- **WHEN** output cannot be written due to disk space
- **THEN** job fails with appropriate error message

### Requirement: Concurrent Job Limiting
The system SHALL limit concurrent render jobs to prevent server overload.

#### Scenario: Queue when busy
- **WHEN** maximum concurrent jobs reached
- **THEN** new jobs remain in "pending" status until slot available

#### Scenario: Process queued job
- **WHEN** a running job completes
- **THEN** next pending job starts automatically

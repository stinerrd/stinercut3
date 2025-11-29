## ADDED Requirements

### Requirement: Project Creation
The system SHALL allow users to create new projects with a name.

#### Scenario: Create project with name
- **WHEN** user submits project creation form with name "My Skydive Video"
- **THEN** the system creates a new project and redirects to project detail page

#### Scenario: Create project with empty name
- **WHEN** user submits project creation form with empty name
- **THEN** the system returns validation error

### Requirement: Project Listing
The system SHALL display a list of all projects with name, creation date, and status.

#### Scenario: View project list
- **WHEN** user navigates to projects page
- **THEN** the system displays all projects sorted by creation date (newest first)

#### Scenario: Empty project list
- **WHEN** user has no projects
- **THEN** the system displays message "No projects yet" with create button

### Requirement: Project Deletion
The system SHALL allow users to delete projects and all associated data.

#### Scenario: Delete project
- **WHEN** user confirms project deletion
- **THEN** the system deletes project, all videos, jobs, and files from storage

#### Scenario: Delete project confirmation
- **WHEN** user clicks delete button
- **THEN** the system shows confirmation dialog before deletion

### Requirement: Video Upload
The system SHALL accept video file uploads in MP4, MOV, and MKV formats.

#### Scenario: Upload single video
- **WHEN** user uploads a valid MP4 file
- **THEN** the system stores file in /shared-videos/uploads/{project_id}/, extracts metadata, and creates video record

#### Scenario: Upload multiple videos
- **WHEN** user uploads 5 video files at once
- **THEN** the system processes all files and adds them to project in upload order

#### Scenario: Upload invalid format
- **WHEN** user uploads a .txt file
- **THEN** the system returns error "Invalid file format. Supported: MP4, MOV, MKV"

#### Scenario: Upload too short video
- **WHEN** user uploads video shorter than 5 seconds
- **THEN** the system returns error "Video must be at least 5 seconds long"

### Requirement: Video Metadata Extraction
The system SHALL extract video metadata using ffprobe: duration, width, height, codec, fps, audio codec.

#### Scenario: Extract metadata from H.264 video
- **WHEN** an H.264 MP4 video is uploaded
- **THEN** the system extracts duration (seconds), resolution (1920x1080), codec (h264), fps (30), and audio codec (aac)

#### Scenario: Extract metadata from HEVC video
- **WHEN** an HEVC/H.265 video is uploaded
- **THEN** the system correctly identifies codec as "hevc"

### Requirement: Video Thumbnail Generation
The system SHALL generate thumbnail images for uploaded videos.

#### Scenario: Generate thumbnail
- **WHEN** a video is uploaded
- **THEN** the system extracts frame at 1 second mark and saves as JPEG thumbnail

#### Scenario: Thumbnail for short video
- **WHEN** a 3-second video is uploaded
- **THEN** the system extracts frame at 0.5 second mark

### Requirement: Video Listing
The system SHALL display all videos in a project with thumbnails, filename, and duration.

#### Scenario: View video list
- **WHEN** user views project detail page
- **THEN** the system displays all videos in order with thumbnails and metadata

### Requirement: Video Reordering
The system SHALL allow users to change the order of videos in a project.

#### Scenario: Drag-drop reorder
- **WHEN** user drags video from position 3 to position 1
- **THEN** the system updates order field for affected videos

#### Scenario: Persist order
- **WHEN** user reorders videos and refreshes page
- **THEN** the system displays videos in the new order

### Requirement: Video Removal
The system SHALL allow users to remove individual videos from a project.

#### Scenario: Remove video
- **WHEN** user clicks remove on a video
- **THEN** the system deletes video record and file from storage

#### Scenario: Remove and reorder
- **WHEN** user removes video at position 2 of 5
- **THEN** remaining videos are renumbered to positions 1, 2, 3, 4

### Requirement: Video Duration Validation
The system SHALL validate minimum video duration of 5 seconds (configurable).

#### Scenario: Reject short video
- **WHEN** video duration is 3 seconds and minimum is 5
- **THEN** the system rejects upload with error message

#### Scenario: Accept valid duration
- **WHEN** video duration is 60 seconds
- **THEN** the system accepts the upload

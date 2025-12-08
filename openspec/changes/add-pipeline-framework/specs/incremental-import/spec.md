# incremental-import Specification

## Purpose
Smart incremental import system that avoids copying already-imported videos from SD cards. Supports TMs who do multiple jumps per day on the same card.

## ADDED Requirements

### Requirement: Imported File Tracking
The system SHALL track imported files with: id, filename, file_size, file_modified_date, file_hash (optional), source_device, import_date, pipeline_execution_id.

#### Scenario: Record imported file
- **WHEN** a file is successfully copied from SD card
- **THEN** the system creates an `imported_file` record
- **AND** stores filename, size, and modified date for future matching

#### Scenario: Check if file already imported
- **WHEN** the backend receives a file list from Detector
- **THEN** the system queries `imported_file` table
- **AND** matches by filename + size + modified_date combination
- **AND** returns list of files NOT already imported

### Requirement: File List from Detector
The Detector SHALL send file metadata (not content) when SD card is inserted.

#### Scenario: Detector sends file list
- **GIVEN** an SD card is inserted
- **WHEN** the Detector scans the card
- **THEN** it sends `sd:file_list` WebSocket message with array of:
  - `filename` (string)
  - `size` (bytes)
  - `modified_date` (ISO timestamp)
  - `path` (full path on host)

#### Scenario: Empty or unreadable card
- **GIVEN** an SD card is inserted
- **WHEN** the card is empty or unreadable
- **THEN** the Detector sends `sd:file_list` with empty array
- **AND** includes `error` field if card could not be read

### Requirement: Selective File Copy Request
The backend SHALL request specific files from Detector via WebSocket.

#### Scenario: Request small files first
- **GIVEN** the backend has identified new files
- **WHEN** some files are < 50MB (potential QR videos)
- **THEN** the backend sends `sd:copy_request` for small files first
- **AND** waits for `sd:file_copied` before processing

#### Scenario: Request remaining files
- **GIVEN** QR video has been processed
- **WHEN** session videos are identified
- **THEN** the backend sends `sd:copy_request` for remaining new files

#### Scenario: Copy request format
- **WHEN** `sd:copy_request` is sent
- **THEN** it contains:
  - `files`: array of filenames to copy
  - `destination`: path in /shared-videos/incoming/
  - `message_id`: correlation ID for tracking

### Requirement: Copy Completion Notification
The Detector SHALL notify backend when files are copied.

#### Scenario: File copied successfully
- **GIVEN** the Detector receives `sd:copy_request`
- **WHEN** a file is copied to shared volume
- **THEN** the Detector sends `sd:file_copied` with:
  - `filename`: original filename
  - `destination_path`: full path in shared volume
  - `size`: bytes copied
  - `message_id`: correlation ID

#### Scenario: Copy error
- **GIVEN** the Detector receives `sd:copy_request`
- **WHEN** a file fails to copy
- **THEN** the Detector sends `sd:copy_error` with:
  - `filename`: file that failed
  - `error`: error message
  - `message_id`: correlation ID

### Requirement: QR Code Video Detection
The system SHALL identify potential QR code videos by file size.

#### Scenario: Identify QR videos
- **GIVEN** a list of new files
- **WHEN** files are sorted by size
- **THEN** files < 50MB are flagged as potential QR videos
- **AND** processed first before larger session videos

#### Scenario: Multiple QR videos per session
- **GIVEN** multiple small videos exist
- **WHEN** each is processed for QR codes
- **THEN** videos are grouped by QR content (booking_id)
- **AND** subsequent large videos are associated with the correct session

### Requirement: QR Code Decoding
The system SHALL extract and decode QR codes from video files.

#### Scenario: Extract frames from video
- **GIVEN** a potential QR video file
- **WHEN** the decode_qr step runs
- **THEN** FFmpeg extracts frames from first 5 seconds (every 0.5s = 10 frames)
- **AND** frames are passed to QR decoder

#### Scenario: Decode QR successfully
- **GIVEN** extracted video frames
- **WHEN** pyzbar finds a QR code
- **THEN** the QR data is parsed as JSON
- **AND** expected fields: `passenger_name`, `booking_id`, `tandem_master_id`, `jump_date`

#### Scenario: No QR found
- **GIVEN** extracted video frames
- **WHEN** no QR code is detected in any frame
- **THEN** the step logs a warning
- **AND** marks the file as "no_qr_found" for manual review

#### Scenario: Invalid QR data
- **GIVEN** a QR code is decoded
- **WHEN** the data is not valid JSON or missing required fields
- **THEN** the step logs the raw QR content
- **AND** marks the file for manual review

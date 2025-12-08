# pipeline-execution Specification

## Purpose
Event-driven video processing pipeline framework for the backend. Manages pipeline lifecycle from trigger through completion, with support for parallel step execution and dependency resolution.

## ADDED Requirements

### Requirement: Pipeline Execution Model
The system SHALL store pipeline executions with: id, uuid, message_id (detector correlation), pipeline_type, status (pending/running/completed/failed/cancelled), job_id (nullable FK to job), execution_data (JSON), error_message, timestamps.

#### Scenario: Create pipeline execution
- **WHEN** a detector signal triggers a pipeline
- **THEN** the system creates a pipeline_execution record with status "running"
- **AND** stores the message_id for frontend correlation
- **AND** initializes execution_data with trigger payload (e.g., sd_path)

#### Scenario: Pipeline completion
- **WHEN** all pipeline steps complete successfully
- **THEN** the system sets status to "completed"
- **AND** execution_data contains merged output from all steps

#### Scenario: Pipeline failure
- **WHEN** any required step fails
- **THEN** the system sets status to "failed"
- **AND** stores the error_message with step details

### Requirement: Detector Signal Trigger
The system SHALL start a pipeline when receiving a `detector:sd_inserted` WebSocket message.

#### Scenario: SD card detection triggers pipeline
- **GIVEN** the backend WebSocket receives a `detector:sd_inserted` message
- **WHEN** the message contains `message_id` and `sd_path`
- **THEN** the orchestrator creates a pipeline_execution
- **AND** creates initial steps (scan_sd, create_job, copy_files)
- **AND** broadcasts `pipeline:started` to frontend

### Requirement: Pipeline Progress Broadcasting
The system SHALL broadcast pipeline progress events via WebSocket.

#### Scenario: Step completion broadcast
- **GIVEN** a pipeline is running
- **WHEN** a step completes
- **THEN** the system broadcasts `pipeline:step_completed` with execution_id, step_name, and progress percentage

#### Scenario: Pipeline completion broadcast
- **GIVEN** a pipeline is running
- **WHEN** all steps complete
- **THEN** the system broadcasts `pipeline:completed` with execution_id

#### Scenario: Pipeline failure broadcast
- **GIVEN** a pipeline is running
- **WHEN** a step fails
- **THEN** the system broadcasts `pipeline:failed` with execution_id and error details

### Requirement: Execution Data Accumulation
The system SHALL merge step outputs into execution_data as steps complete.

#### Scenario: Step output merging
- **GIVEN** a step completes successfully
- **WHEN** the step returns output_data
- **THEN** the scheduler merges output_data into execution.execution_data
- **AND** subsequent steps receive the accumulated data

### Requirement: Pipeline API Endpoints
The system SHALL provide REST endpoints for pipeline status and management.

#### Scenario: Get pipeline status
- **WHEN** GET `/api/pipeline/{execution_id}` is called
- **THEN** the system returns execution status, step statuses, and progress

#### Scenario: Retry failed pipeline
- **WHEN** POST `/api/pipeline/{execution_id}/retry` is called
- **AND** the pipeline status is "failed"
- **THEN** the system resets the failed step to "pending"
- **AND** resumes execution from that step

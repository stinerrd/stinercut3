# pipeline-steps Specification

## Purpose
Step execution framework for pipelines. Handles step lifecycle, dependency resolution, parallel execution via Redis queue, and dynamic step spawning.

## ADDED Requirements

### Requirement: Pipeline Step Model
The system SHALL store pipeline steps with: id, execution_id (FK), step_name, step_key (unique within execution), status (pending/queued/running/completed/failed), depends_on (JSON array of step_keys), params (JSON), input_data, output_data, worker_id, error_message, attempt, timestamps.

#### Scenario: Create step with dependencies
- **WHEN** a step is created with depends_on array
- **THEN** the step status is set to "pending"
- **AND** the step will not be queued until all dependencies complete

#### Scenario: Parameterized step key
- **WHEN** a step is created with params (e.g., file_path)
- **THEN** step_key is set to "step_name:param_identifier"
- **AND** step_key is unique within the execution

### Requirement: Step Dependency Resolution
The system SHALL queue steps only when all dependencies are satisfied.

#### Scenario: Queue step with no dependencies
- **GIVEN** a step has no depends_on or empty array
- **WHEN** the scheduler runs
- **THEN** the step is immediately queued to Redis

#### Scenario: Queue step after dependencies complete
- **GIVEN** a step depends on ["scan_sd", "copy_files"]
- **WHEN** both scan_sd and copy_files complete
- **THEN** the scheduler queues the step to Redis
- **AND** sets input_data to current execution_data

#### Scenario: Parallel steps with same dependency
- **GIVEN** steps A and B both depend only on step X
- **WHEN** step X completes
- **THEN** both A and B are queued simultaneously
- **AND** can be processed by different workers

### Requirement: Redis Queue Integration
The system SHALL use Redis for step queue management.

#### Scenario: Push step to queue
- **WHEN** a step is ready for execution
- **THEN** the scheduler pushes to Redis queue "pipeline:steps"
- **AND** the message contains step_id, step_name, execution_id

#### Scenario: Worker pulls from queue
- **WHEN** a worker calls BRPOP on "pipeline:steps"
- **THEN** the worker receives the next step to process
- **AND** sets step status to "running" with worker_id

### Requirement: Dynamic Step Spawning
Steps SHALL be able to spawn new steps during execution.

#### Scenario: Spawn step during execution
- **GIVEN** a step is executing (e.g., copy_files)
- **WHEN** the step calls spawn_step() with NewStep(name, depends_on, params)
- **THEN** a new pipeline_step record is created
- **AND** if dependencies are met, the step is immediately queued

#### Scenario: Copy file spawns metadata extraction
- **GIVEN** copy_files step is copying multiple videos
- **WHEN** each file finishes copying
- **THEN** spawn_step() creates an extract_metadata step for that file
- **AND** the metadata step can start immediately (no deps)

### Requirement: Step Execution by Workers
Workers SHALL execute steps and report completion.

#### Scenario: Successful step execution
- **GIVEN** a worker pulls a step from Redis
- **WHEN** the step executes successfully
- **THEN** the worker sets status to "completed"
- **AND** stores output_data
- **AND** notifies the scheduler via on_step_completed()

#### Scenario: Failed step execution
- **GIVEN** a worker pulls a step from Redis
- **WHEN** the step execution raises an exception
- **THEN** the worker sets status to "failed"
- **AND** stores error_message
- **AND** marks the pipeline execution as "failed"

### Requirement: Step Logging
The system SHALL log step lifecycle events.

#### Scenario: Log step queued
- **WHEN** a step is queued to Redis
- **THEN** a pipeline_step_log record is created with event_type "queued"

#### Scenario: Log step started
- **WHEN** a worker starts executing a step
- **THEN** a log record is created with event_type "started" and worker_id

#### Scenario: Log step completed
- **WHEN** a step completes successfully
- **THEN** a log record is created with event_type "completed"

#### Scenario: Log step failed
- **WHEN** a step fails
- **THEN** a log record is created with event_type "failed" and error details

### Requirement: BaseStep Abstract Class
All pipeline steps SHALL inherit from BaseStep with dependency and spawn support.

#### Scenario: Step declares dependencies
- **GIVEN** a step class inherits from BaseStep
- **WHEN** the class defines `depends_on = ["scan_sd"]`
- **THEN** instances of this step require scan_sd to complete first

#### Scenario: Step executes with context
- **GIVEN** a step class implements execute()
- **WHEN** execute(execution_id, execution_data) is called
- **THEN** the step can access accumulated data from previous steps
- **AND** can call spawn_step() to create new steps
- **AND** returns StepResult with success, output_data, and optional error_message

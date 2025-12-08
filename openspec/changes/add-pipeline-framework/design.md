# Design: Video Processing Pipeline Framework

## Context

Stinercut needs automated video processing triggered by SD card insertion. Key constraints:
- **Cross-platform**: Must work on Linux and Windows (Docker Desktop)
- **Incremental import**: TM does 10+ jumps/day on same SD card; only copy NEW videos
- **QR-based identification**: Small video before each jump contains QR code with passenger/booking info
- **Detector copies files**: Backend cannot access SD card directly; Detector (host service) handles file copying

### Workflow

1. **SD card inserted** → Detector scans files, sends metadata list to backend
2. **Backend filters** → Checks `imported_file` table, identifies NEW files
3. **Request small files** → Backend asks Detector to copy QR videos first (< 50MB)
4. **QR decode** → Backend extracts frame, decodes QR → passenger name, booking ID
5. **Request remaining** → Backend asks Detector to copy other NEW videos for this session
6. **Process videos** → Pipeline applies intro, watermark, splashscreen, renders output

Steps have dependencies but some can run in parallel. Steps can spawn new steps dynamically.

## Goals / Non-Goals

**Goals:**
- Event-driven pipeline triggered by WebSocket detector signal
- Parallel step execution with explicit dependency declaration
- Dynamic step spawning during execution
- Retry from failed step without restarting pipeline
- Multi-worker support via Redis queue
- Real-time progress updates via WebSocket
- **Smart incremental import** - only copy files not already in database
- **QR code recognition** - extract passenger/booking data from video
- **Cross-platform** - Linux and Windows support via Detector file copying

**Non-Goals:**
- GUI for pipeline definition (pipelines defined in Python code)
- Pipeline versioning or rollback
- Cross-pipeline dependencies
- Step timeout handling (future enhancement)
- Direct SD card access from container (Detector handles this)

## Decisions

### Decision 1: Redis Queue for Multi-Worker Support
**What**: Use Redis as a job queue for step execution.
**Why**: Allows multiple workers to process steps in parallel. Essential for CPU-intensive FFmpeg operations. Single-worker WebSocket constraint doesn't affect pipeline workers.
**Alternatives**:
- Celery: Too heavy for this use case
- asyncio only: Can't scale to multiple processes for FFmpeg

### Decision 2: Step Dependencies via `depends_on` Array
**What**: Each step declares which step_keys must complete before it can run.
**Why**: Simple, explicit dependency model. Scheduler checks completed steps and queues ready ones.
**Alternatives**:
- DAG library: Overkill for this use case
- Sequential-only: Loses parallelism benefits

### Decision 3: Dynamic Step Spawning via `spawn_step()`
**What**: Steps can create new steps during execution with immediate queuing.
**Why**: Enables fine-grained parallelism (e.g., start processing video1 while copying video2).
**Alternatives**:
- Pre-defined step list only: Loses optimization opportunity
- Callback pattern: More complex, harder to persist state

### Decision 4: Unique `step_key` for Parameterized Steps
**What**: Steps use `step_name:param_hash` format for uniqueness (e.g., `extract_metadata:video1.mp4`).
**Why**: Multiple instances of same step type need unique identifiers for dependency resolution.
**Alternatives**:
- Sequential IDs only: Loses semantic meaning in dependencies

### Decision 5: Pipelines Defined in Python Code
**What**: Pipeline definitions (which steps, default dependencies) are Python code, not database records.
**Why**: Version controlled, type-safe, easier to test. No need for runtime pipeline modification.
**Alternatives**:
- Database definitions: Adds complexity without clear benefit

## Architecture

```
┌─────────────────┐                              ┌─────────────────┐
│  SD Card        │                              │    Frontend     │
│  /media/sdX     │                              │   (Browser)     │
└────────┬────────┘                              └────────▲────────┘
         │                                                │
         │ file access                                    │ WebSocket
         ▼                                                │
┌─────────────────┐      WebSocket (bidirectional)       │
│ Device Detector │ ◄──────────────────────────────────► │
│  (Host Service) │                                      │
└────────┬────────┘                                      │
         │                                               │
         │ 1. Send file list                             │
         │ 2. Receive copy requests                      │
         │ 3. Copy files to shared volume                │
         ▼                                               │
┌─────────────────┐     WebSocket      ┌─────────────────┤
│ /shared-videos/ │ ◄───────────────── │    Backend      │
│  (Docker Vol)   │    copy request    │   (FastAPI)     │
└─────────────────┘                    └────────┬────────┘
                                                │
                                                │ Push to Redis
                                                ▼
                                       ┌─────────────────┐
                                       │   Redis Queue   │
                                       └────────┬────────┘
                                                │
                                    ┌───────────┼───────────┐
                                    ▼           ▼           ▼
                              ┌─────────┐ ┌─────────┐ ┌─────────┐
                              │Worker 1 │ │Worker 2 │ │Worker 3 │
                              └─────────┘ └─────────┘ └─────────┘
```

### Message Flow

```
Detector                    Backend                     Frontend
   │                           │                           │
   │──── sd:file_list ────────►│                           │
   │     (metadata only)       │                           │
   │                           │── check imported_file ───►│
   │                           │                           │
   │◄─── sd:copy_request ──────│                           │
   │     (small files first)   │                           │
   │                           │                           │
   │──── sd:file_copied ──────►│                           │
   │     (to /shared-videos)   │                           │
   │                           │── decode QR ─────────────►│
   │                           │                           │
   │◄─── sd:copy_request ──────│                           │
   │     (remaining videos)    │                           │
   │                           │                           │
   │──── sd:file_copied ──────►│── pipeline:progress ─────►│
   │                           │                           │
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| Orchestrator | Receives detector signal, creates execution and initial steps |
| Scheduler | Resolves dependencies, queues ready steps to Redis |
| Worker | Pulls steps from Redis, executes, reports completion |
| Registry | Maps step names to step classes |
| BaseStep | Abstract base class with spawn_step() capability |

### Data Flow

1. Detector sends `detector:sd_inserted` via WebSocket
2. Orchestrator creates `pipeline_execution` + initial `pipeline_step` records
3. Scheduler finds steps with no/satisfied dependencies, pushes to Redis
4. Worker pulls step, executes, calls `on_step_completed`
5. Scheduler merges output into `execution_data`, queues newly ready steps
6. Repeat until all steps complete or one fails

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Redis single point of failure | Accept for MVP; can add Redis Sentinel later |
| Step failure cascades to whole pipeline | By design: fail-fast prevents wasted processing |
| Dynamic steps complicate retry | Step state fully persisted; retry restarts from failed step |
| Memory pressure with large execution_data | Store file paths, not file contents |

## Migration Plan

1. Add Redis to docker-compose (no data migration needed)
2. Run migration for new tables (additive, no existing data affected)
3. Deploy backend with pipeline package (feature is opt-in via detector signal)
4. No rollback concerns: new tables can be dropped if needed

## Open Questions

- Should we add step timeout support? (Deferred to future enhancement)
- Maximum retry attempts per step? (Suggest 3, configurable per step)
- Should failed pipelines auto-cleanup temp files? (Suggest yes, in cleanup step)

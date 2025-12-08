## QR Code Feature Design

### Context

Workloads are time-bounded sessions for tandem skydiving video editing. Operators need a portable way to reference workloads without manually entering identifiers. QR codes provide this functionality at workload creation time.

### Goals

- Provide scannable QR code for each workload for field use
- Reduce manual data entry and identification errors
- Maintain backward compatibility with existing workloads
- Minimize performance impact (generate once at creation)

### Non-Goals

- Bulk QR code generation for existing workloads
- Dynamic QR code updates when workload changes
- Alternative QR code content or encoding formats
- Mobile app integration (read QR codes via phone)

### Technical Decisions

#### Decision 1: Generate QR at Creation Time
**What**: QR code generated in `WorkloadService::create()` immediately after UUID assignment
**Why**:
- Avoids on-demand generation overhead
- Ensures every new workload has a QR code
- Simplifies caching and retrieval
**Alternatives Considered**:
- On-demand generation: More flexible but slower for display
- Batch generation: Requires separate job, unnecessary complexity

#### Decision 2: Store as BLOB
**What**: Store QR PNG image binary data in `workloads.qr` BLOB column
**Why**:
- Immediate availability without regeneration
- Self-contained, no external service dependency
- Simple to retrieve and display
**Alternatives Considered**:
- Generate on-the-fly from UUID: Possible but adds latency
- Store as external file: Adds filesystem complexity

#### Decision 3: Text Content Format
**What**: QR code contains "Stinercut: [WORKLOAD_UUID]" text
**Why**:
- Clear branding ("Stinercut" label)
- Unique identifier (UUID)
- Human-readable if decoded manually
- URL format not needed (UUID is sufficient for lookup)

#### Decision 4: Modal Display
**What**: Bootstrap modal for QR code preview in table UI
**Why**:
- Consistent with existing AdminLTE 3 + Bootstrap pattern
- Non-intrusive (doesn't replace table row)
- Easy to implement with Stimulus controller
**Alternatives Considered**:
- Inline display in table: Clutters UI
- Separate page: Requires navigation

### Data Model

```
Workload Entity:
- id: int (primary key)
- uuid: string (unique, RFC 4122)
- qr: BLOB (nullable, stores PNG image)
- ... existing fields ...

QrCodeService:
- generateQrCode(uuid: string): string (returns PNG BLOB)
```

### Architecture

```
WorkloadController (HTTP request)
  ↓
WorkloadService (business logic)
  ├→ QrCodeService (QR generation)
  ├→ WorkloadRepository (persistence)
  ↓
Workload Entity (model)
  ↓
Database (MySQL: workloads.qr BLOB)
```

### UI Flow

1. User views workloads table
2. Each row shows "View QR" button
3. User clicks button → Stimulus controller intercepts
4. Controller fetches QR code (base64 or data-url from entity)
5. Bootstrap modal displays QR image
6. User can scan with phone or print for field reference

### Migration Strategy

**Backward Compatibility**:
- `qr` column is nullable
- Existing workloads have NULL `qr` value
- UI shows "No QR available" for NULL rows
- No data backfill needed
- No schema changes for other tables

**Deployment**:
1. Deploy migration to add `qr` BLOB column
2. Deploy updated Workload entity + QrCodeService
3. Deploy updated WorkloadService (uses QrCodeService on create)
4. Deploy UI updates (table button + modal)
5. No downtime; existing workloads unaffected

### Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| QR generation fails on create | Wrap in try-catch; log error; set `qr = NULL`; allow workload creation to succeed |
| BLOB storage too large | PNG is typically <5KB; no size concern at scale |
| UUID encoding issue | Use standard `Symfony\Component\Uid\Uuid` which produces RFC 4122 format |
| Modal not displaying | Test with multiple browsers; use standard Bootstrap 5 modal API |
| Backward compatibility broken | Keep `qr` nullable; test with old workloads; no migrations on read |

### Performance Considerations

- QR generation: One-time at creation (~5-10ms per workload)
- Storage: PNG BLOB ~5KB per workload
- Retrieval: BLOB fetch from DB, no extra queries
- Display: Base64 encode for inline image in HTML, no additional HTTP request
- Scaling: No performance impact beyond storage; QR generation is negligible overhead

### Open Questions

1. Should QR code be downloadable/printable? (Out of scope, can add later)
2. Should QR code contain URL (e.g., `https://stinercut.local/workload/[uuid]`)? (Using text "Stinercut: [UUID]" per requirements)
3. Should users be able to regenerate/reset QR code? (No—immutable per creation)

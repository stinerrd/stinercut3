# Proposal: Add Workloads Management

## Summary
Add a Workloads feature to track tandem skydiving work items with video/photo preferences, marketing consent, and daily scheduling. Workloads are associated with tandem masters and support filtering, pagination, and full CRUD operations.

## Motivation
The application needs to track individual tandem skydiving sessions (workloads) to manage video/photo production workflow. Each workload represents a customer session that may require video editing, photo processing, or both. The marketing flag tracks customer consent for promotional use.

## Scope

### In Scope
- Database table for workloads with all required fields
- Domain entity, repository, and service following existing patterns
- Web controller and API endpoints for CRUD operations
- AdminLTE UI with collapsible filters and AJAX pagination
- Filtering by date (default: today), status, tandem master, video/photo preference

### Out of Scope
- Integration with video processing pipeline (future work)
- Bulk operations on workloads
- Export/import functionality
- Customer notifications

## Key Design Decisions

1. **Status as VARCHAR, not ENUM**: Allows adding new statuses without database migration
2. **UUIDv4 generated in PHP**: Using Symfony's Uid component for consistency
3. **Nullable TandemMaster relationship**: Workloads can exist without assigned tandem master; ON DELETE SET NULL preserves workloads when tandem master is deleted
4. **AJAX pagination with HTML responses**: Following skydivelog2 patterns for smooth UX with browser history support
5. **Collapsible filter panel**: Reduces visual clutter while keeping filters accessible
6. **Status not editable in UI**: Status is always set to "created" on new workloads and will be changed by backend processing only - not exposed in create/edit forms

## Dependencies
- Existing TandemMaster entity (for relationship)
- AdminLTE frontend templates
- Pagination JavaScript utilities (adapted from skydivelog2)

## Risks
- **Low**: Standard CRUD feature following established patterns
- **Medium**: Pagination JS may need adaptation from skydivelog2 to stinercut patterns

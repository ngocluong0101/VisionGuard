# VisionGuard Database

## Purpose

VisionGuard stores structured metadata in PostgreSQL and keeps media files in local storage or object storage. The database is intentionally limited to entities that need querying, relationships, and auditability.

## Entities

- Location
- Camera
- Zone
- Event
- Recording

## Relationships

- A Location can have many Cameras.
- A Camera can have many Zones, Events, and Recordings.
- A Recording can optionally point to an Event.

```mermaid
erDiagram
    LOCATION ||--o{ CAMERA : has
    CAMERA ||--o{ ZONE : has
    CAMERA ||--o{ EVENT : has
    CAMERA ||--o{ RECORDING : has
    EVENT ||--o{ RECORDING : references
```

## Storage Strategy

- PostgreSQL stores metadata, timestamps, enums, and file path references.
- Snapshot images and video clips live in `storage/` or external object storage.
- Frame-by-frame detections are not persisted in PostgreSQL.

## Zone Coordinate Strategy

- Zone coordinates are stored as JSON arrays of normalized points.
- Normalized values stay in the `0..1` range so zone definitions remain resolution-independent.
- The same Zone model supports restricted areas, loitering regions, and line-crossing configurations in MVP form.

## Migration Commands

```bash
alembic upgrade head
alembic downgrade -1
```

Set `DATABASE_URL` before running migrations, for example:

```bash
export DATABASE_URL=postgresql+psycopg://visionguard:password@localhost:5432/visionguard
```

## Notes

- Media file contents are never stored directly in PostgreSQL.
- Foreign keys are configured to preserve metadata when parent records are deleted.
- The MVP avoids PostGIS so the schema stays simple and portable.

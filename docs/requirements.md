# VisionGuard Requirements

## Purpose

VisionGuard is an AI-powered enterprise video surveillance platform focused on monitoring, event detection, and evidence management for security operations.

## MVP Scope

### Video Sources

- Local `.mp4` file upload for offline testing.
- Webcam capture for direct machine input.
- RTSP/IP camera for live deployment.

### Core Capabilities

- Manage multiple cameras and video sources.
- Associate cameras with locations and areas.
- Show camera online/offline state.
- Run live monitoring with shared AI processing.
- Detect `person`, `car`, `motorcycle`, `bus`, and `truck`.
- Track multiple objects across frames.
- Generate intrusion, line crossing, and loitering events.
- Capture snapshot and video evidence.
- Browse event history with search and filters.
- Display basic analytics.

## Exclusions From MVP

- Login/logout.
- Authentication.
- Authorization and RBAC.
- User management.
- Face recognition.
- License plate recognition.
- PPE detection.
- Fire and smoke detection.

## Domain Model

### Location

Represents a physical site, building, floor, or zone grouping.

### Camera / VideoSource

Represents a local file, webcam, or RTSP source. Camera metadata includes name, source type, location, and operational state.

### Zone

Represents a restricted area or monitoring region. Used by intrusion and loitering rules.

### Event

Represents a generated security event such as intrusion, line crossing, or loitering.

### Recording

Represents evidence artifacts such as snapshots or video clips.

## Event Rules

### Intrusion

- Trigger condition: a tracked object enters a restricted zone.
- Required data: zone geometry, tracked object position, object identity, frame timestamps.
- Event output: intrusion event with source, zone, track reference, timestamp, and evidence reference.

### Line Crossing

- Trigger condition: a tracked object crosses a configured line in the defined direction.
- Required data: line geometry, track trajectory, frame timestamps.
- Event output: line crossing event with direction, source, track reference, timestamp, and evidence reference.

### Loitering

- Trigger condition: a tracked object remains inside a monitored zone longer than the configured threshold.
- Required data: zone geometry, track dwell time, frame timestamps.
- Event output: loitering event with duration, source, track reference, timestamp, and evidence reference.

## Data Storage Rules

- Do not store every frame-level detection in PostgreSQL.
- Persist only metadata needed for cameras, zones, events, and evidence references.
- Store snapshots and video clips in file or object storage.
- Keep detection and tracking state ephemeral unless a small persistent subset is needed for event creation or analytics.

## Non-Functional Requirements

- Realtime processing should keep the ingest, inference, tracking, and event pipeline responsive under normal operating load.
- Camera reconnect behavior should retry safely and recover from transient stream failures.
- Error handling should isolate a failed camera from the rest of the system.
- Logging should capture source lifecycle, inference errors, event generation, and storage operations.
- Performance should favor shared pipeline design, bounded buffering, and minimal database writes.
- Scalability should come from modular boundaries, source-level concurrency, and externalized storage.
- Maintainability should come from clear module separation, typed contracts, and a shared data model.

## Future Improvements

- Authentication and RBAC.
- Advanced analytics.
- Additional event types.
- Model versioning and A/B evaluation.
- Retention policies for evidence.

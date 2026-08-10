# VisionGuard

AI-powered enterprise video surveillance and monitoring platform.

## Overview

VisionGuard is being built as a modular monolith for enterprise video monitoring. Phase 03 adds the database layer, SQLAlchemy models, Alembic migration foundation, and CRUD APIs for the core metadata entities. The AI pipeline, camera processing, event engine, and UI remain planned for later phases.

## Problem

Security teams need a platform that can eventually ingest multiple video sources, run a shared CV pipeline, and surface security events with evidence. The current codebase now supports structured metadata management for the core domain without adding video processing logic yet.

## Implemented

- Phase 01 requirements and architecture docs.
- Phase 02 backend foundation, config, logging, and health check.
- Phase 03 SQLAlchemy models, Alembic foundation, and CRUD APIs.

## Planned

- Multi-source video ingestion.
- `.mp4` upload handling.
- Webcam and RTSP capture.
- YOLO detection.
- Multi-object tracking.
- Event detection and evidence generation.
- Analytics and dashboard UI.
- Authentication and authorization.

## Supported Video Sources

Planned sources remain:

- Local `.mp4` file upload.
- Webcam.
- RTSP/IP camera.

The shared source abstraction is designed so all of them can later feed the same processing pipeline.

## High-Level Architecture

- Backend handles app startup, config, health, and API routing.
- SQLAlchemy manages the database layer.
- Alembic manages schema migrations.
- PostgreSQL stores structured metadata.
- File storage folders hold uploads, event snapshots, and recordings.
- Realtime communication and AI processing are planned for later phases.

## API Endpoints Implemented

- `GET /`
- `GET /health`
- `GET /api/v1/locations`
- `GET /api/v1/locations/{id}`
- `POST /api/v1/locations`
- `PATCH /api/v1/locations/{id}`
- `DELETE /api/v1/locations/{id}`
- `GET /api/v1/cameras`
- `GET /api/v1/cameras/{id}`
- `POST /api/v1/cameras`
- `PATCH /api/v1/cameras/{id}`
- `DELETE /api/v1/cameras/{id}`
- `GET /api/v1/zones`
- `GET /api/v1/zones/{id}`
- `POST /api/v1/zones`
- `PATCH /api/v1/zones/{id}`
- `DELETE /api/v1/zones/{id}`
- `GET /api/v1/events`
- `GET /api/v1/events/{id}`
- `POST /api/v1/events`
- `PATCH /api/v1/events/{id}`
- `DELETE /api/v1/events/{id}`
- `GET /api/v1/recordings`
- `GET /api/v1/recordings/{id}`
- `POST /api/v1/recordings`
- `PATCH /api/v1/recordings/{id}`
- `DELETE /api/v1/recordings/{id}`

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Pydantic Settings
- Python Dotenv
- Uvicorn
- PostgreSQL
- React + Vite for later phases
- WebSocket for later phases
- Docker for later phases

## Project Structure

```text
visionguard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── migrations/
│   └── tests/
├── docs/
├── storage/
│   ├── events/
│   ├── recordings/
│   └── uploads/
├── alembic.ini
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Development Setup

The workspace is using a Conda environment named `ai` with Python 3.10.19.

Install dependencies with:

```bash
/home/ngocluong/anaconda3/envs/ai/bin/python -m pip install -r requirements.txt
```

## Environment Configuration

Copy `.env.example` to `.env` and set `DATABASE_URL` for PostgreSQL. Do not commit `.env` or any secrets.

## Database Setup

Run migrations after setting `DATABASE_URL`:

```bash
alembic upgrade head
```

Migration rollback for local development:

```bash
alembic downgrade -1
```

## How to Run Backend

Start the backend from the repository root:

```bash
uvicorn backend.app.main:app --reload
```

## Health Check

After starting the backend, open:

- `GET /`
- `GET /health`

## Current Project Status

Implemented:

- Phase 01 documentation.
- Phase 02 backend foundation and workspace skeleton.
- Phase 03 database layer, migrations, and CRUD foundation.

Planned:

- AI detection and tracking.
- Camera/video ingestion.
- Event detection and evidence capture.
- Frontend UI.
- Authentication.

See [docs/requirements.md](docs/requirements.md), [docs/architecture.md](docs/architecture.md), and [docs/database.md](docs/database.md) for the current design.

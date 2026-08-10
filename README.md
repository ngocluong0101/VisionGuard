# VisionGuard

AI-powered enterprise video surveillance and monitoring platform.

## Overview

VisionGuard is being built as a modular monolith for enterprise video monitoring. Phase 02 establishes the source code foundation, configuration, logging, and a minimal FastAPI backend. The AI pipeline, camera processing, event engine, and UI remain planned for later phases.

## Problem

Security teams need a platform that can eventually ingest multiple video sources, run a shared CV pipeline, and surface security events with evidence. The current phase prepares the project structure so those capabilities can be added without reworking the foundation.

## MVP Features

Implemented in Phase 02:

- Backend project skeleton.
- Centralized configuration from environment variables.
- Basic logging setup.
- `GET /` project info endpoint.
- `GET /health` health check endpoint.
- Local storage placeholders for uploads, events, and recordings.
- Minimal backend tests.

Planned for later phases:

- Multi-source video ingestion.
- `.mp4` upload handling.
- Webcam and RTSP capture.
- YOLO detection.
- Multi-object tracking.
- Event detection and evidence generation.
- Analytics and dashboard UI.

## Supported Video Sources

Planned sources remain:

- Local `.mp4` file upload.
- Webcam.
- RTSP/IP camera.

The shared source abstraction is designed so all of them can later feed the same processing pipeline.

## High-Level Architecture

- Backend handles app startup, config, and health endpoints.
- API routing is prepared for future expansion.
- PostgreSQL is reserved for later metadata storage.
- File storage folders are reserved for uploads, event snapshots, and recordings.
- Realtime communication and AI processing are planned for later phases.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Pydantic Settings
- Python Dotenv
- Uvicorn
- PostgreSQL for later phases
- React + Vite for later phases
- WebSocket for later phases
- Docker for later phases

## Project Structure

```text
visionguard/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   └── core/
│   └── tests/
├── docs/
├── storage/
│   ├── events/
│   ├── recordings/
│   └── uploads/
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

Copy `.env.example` to `.env` and adjust values for local development. Do not commit `.env` or any secrets.

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

Planned:

- AI detection and tracking.
- Camera/video ingestion.
- Event detection and evidence capture.
- Database schema and business logic.
- Frontend UI.
- Authentication.

See [docs/requirements.md](docs/requirements.md) and [docs/architecture.md](docs/architecture.md) for the Phase 01 design.

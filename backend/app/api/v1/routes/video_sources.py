from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.app.core.config import get_settings
from backend.app.schemas.video_source import VideoUploadRead

router = APIRouter(prefix="/video-sources", tags=["video-sources"])


@router.post("/upload", response_model=VideoUploadRead, status_code=status.HTTP_201_CREATED)
async def upload_video_source(file: UploadFile = File(...)) -> VideoUploadRead:
    settings = get_settings()
    original_name = Path(file.filename or "").name
    if Path(original_name).suffix.lower() != ".mp4":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only .mp4 uploads are supported in MVP")

    if file.content_type not in {None, "video/mp4", "application/octet-stream"}:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only MP4 video uploads are supported in MVP")

    storage_dir = Path.cwd() / settings.storage_dir / "uploads"
    storage_dir.mkdir(parents=True, exist_ok=True)
    destination = storage_dir / f"upload_{Path(original_name).stem}_{uuid4().hex}.mp4"

    max_bytes = settings.max_upload_mb * 1024 * 1024
    written = 0
    try:
        with destination.open("wb") as handle:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_bytes:
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Uploaded file exceeds configured maximum size")
                handle.write(chunk)
    except Exception:
        if destination.exists():
            destination.unlink(missing_ok=True)
        raise

    return VideoUploadRead(
        filename=destination.name,
        storage_path=str(destination.relative_to(Path.cwd())),
        size_bytes=written,
        content_type=file.content_type,
        source_type="VIDEO_FILE",
    )
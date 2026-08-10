from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db, get_video_source_manager
from backend.app.models.camera import Camera
from backend.app.schemas.camera import CameraCreate, CameraRead, CameraUpdate
from backend.app.schemas.video_source import CameraLifecycleRead, CameraMetadataRead, CameraStatusRead
from backend.app.services.crud import create_entity, delete_entity, get_entity, list_entities, update_entity
from backend.app.video.exceptions import SourceAlreadyStartedError, SourceFrameUnavailableError, SourceNotRunningError, VideoSourceError
from backend.app.video.manager import VideoSourceManager

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraRead])
def list_cameras(db: Session = Depends(get_db)) -> list[Camera]:
    return list_entities(db, Camera)


@router.get("/{camera_id}", response_model=CameraRead)
def get_camera(camera_id: int, db: Session = Depends(get_db)) -> Camera:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("", response_model=CameraRead, status_code=status.HTTP_201_CREATED)
def create_camera(payload: CameraCreate, db: Session = Depends(get_db)) -> Camera:
    return create_entity(db, Camera, payload.model_dump())


@router.patch("/{camera_id}", response_model=CameraRead)
def update_camera(camera_id: int, payload: CameraUpdate, db: Session = Depends(get_db)) -> Camera:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return update_entity(db, camera, payload.model_dump(exclude_unset=True))


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(camera_id: int, db: Session = Depends(get_db)) -> Response:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    delete_entity(db, camera)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{camera_id}/start", response_model=CameraLifecycleRead)
def start_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    manager: VideoSourceManager = Depends(get_video_source_manager),
) -> CameraLifecycleRead:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    try:
        state = manager.start(camera)
    except SourceAlreadyStartedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except VideoSourceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CameraLifecycleRead(camera_id=camera_id, status=state.status, message=state.message)


@router.post("/{camera_id}/stop", response_model=CameraLifecycleRead)
def stop_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    manager: VideoSourceManager = Depends(get_video_source_manager),
) -> CameraLifecycleRead:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    try:
        state = manager.stop(camera_id)
    except SourceNotRunningError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CameraLifecycleRead(camera_id=camera_id, status=state.status, message=state.message)


@router.get("/{camera_id}/status", response_model=CameraStatusRead)
def camera_status(
    camera_id: int,
    db: Session = Depends(get_db),
    manager: VideoSourceManager = Depends(get_video_source_manager),
) -> CameraStatusRead:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    state = manager.status(camera_id)
    return CameraStatusRead(camera_id=camera_id, status=state.status, message=state.message)


@router.get("/{camera_id}/metadata", response_model=CameraMetadataRead)
def camera_metadata(
    camera_id: int,
    db: Session = Depends(get_db),
    manager: VideoSourceManager = Depends(get_video_source_manager),
) -> CameraMetadataRead:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    state = manager.metadata(camera_id, camera)
    return CameraMetadataRead(
        camera_id=camera_id,
        status=state.status,
        source_type=state.source_type,
        source_uri=state.source_uri,
        width=state.metadata.width,
        height=state.metadata.height,
        fps=state.metadata.fps,
        frame_count=state.metadata.frame_count,
        duration=state.metadata.duration,
        message=state.message,
    )


@router.get("/{camera_id}/snapshot")
def camera_snapshot(
    camera_id: int,
    db: Session = Depends(get_db),
    manager: VideoSourceManager = Depends(get_video_source_manager),
) -> FastAPIResponse:
    camera = get_entity(db, Camera, camera_id)
    if camera is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")

    try:
        image_bytes = manager.snapshot(camera_id)
    except SourceNotRunningError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SourceFrameUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return FastAPIResponse(content=image_bytes, media_type="image/jpeg")
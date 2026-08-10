from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.models.recording import Recording
from backend.app.schemas.recording import RecordingCreate, RecordingRead, RecordingUpdate
from backend.app.services.crud import create_entity, delete_entity, get_entity, list_entities, update_entity

router = APIRouter(prefix="/recordings", tags=["recordings"])


@router.get("", response_model=list[RecordingRead])
def list_recordings(db: Session = Depends(get_db)) -> list[Recording]:
    return list_entities(db, Recording)


@router.get("/{recording_id}", response_model=RecordingRead)
def get_recording(recording_id: int, db: Session = Depends(get_db)) -> Recording:
    recording = get_entity(db, Recording, recording_id)
    if recording is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
    return recording


@router.post("", response_model=RecordingRead, status_code=status.HTTP_201_CREATED)
def create_recording(payload: RecordingCreate, db: Session = Depends(get_db)) -> Recording:
    return create_entity(db, Recording, payload.model_dump())


@router.patch("/{recording_id}", response_model=RecordingRead)
def update_recording(recording_id: int, payload: RecordingUpdate, db: Session = Depends(get_db)) -> Recording:
    recording = get_entity(db, Recording, recording_id)
    if recording is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
    return update_entity(db, recording, payload.model_dump(exclude_unset=True))


@router.delete("/{recording_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recording(recording_id: int, db: Session = Depends(get_db)) -> Response:
    recording = get_entity(db, Recording, recording_id)
    if recording is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recording not found")
    delete_entity(db, recording)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
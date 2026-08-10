from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.models.zone import Zone
from backend.app.schemas.zone import ZoneCreate, ZoneRead, ZoneUpdate
from backend.app.services.crud import create_entity, delete_entity, get_entity, list_entities, update_entity

router = APIRouter(prefix="/zones", tags=["zones"])


@router.get("", response_model=list[ZoneRead])
def list_zones(db: Session = Depends(get_db)) -> list[Zone]:
    return list_entities(db, Zone)


@router.get("/{zone_id}", response_model=ZoneRead)
def get_zone(zone_id: int, db: Session = Depends(get_db)) -> Zone:
    zone = get_entity(db, Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.post("", response_model=ZoneRead, status_code=status.HTTP_201_CREATED)
def create_zone(payload: ZoneCreate, db: Session = Depends(get_db)) -> Zone:
    return create_entity(db, Zone, payload.model_dump())


@router.patch("/{zone_id}", response_model=ZoneRead)
def update_zone(zone_id: int, payload: ZoneUpdate, db: Session = Depends(get_db)) -> Zone:
    zone = get_entity(db, Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return update_entity(db, zone, payload.model_dump(exclude_unset=True))


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(zone_id: int, db: Session = Depends(get_db)) -> Response:
    zone = get_entity(db, Zone, zone_id)
    if zone is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    delete_entity(db, zone)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
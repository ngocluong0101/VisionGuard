from backend.app.models.enums import CameraStatus
from backend.app.schemas.base import SchemaBaseModel


class VideoUploadRead(SchemaBaseModel):
    filename: str
    storage_path: str
    size_bytes: int
    content_type: str | None = None
    source_type: str = "VIDEO_FILE"


class CameraLifecycleRead(SchemaBaseModel):
    camera_id: int
    status: CameraStatus
    message: str | None = None


class CameraStatusRead(CameraLifecycleRead):
    pass


class CameraMetadataRead(SchemaBaseModel):
    camera_id: int
    status: CameraStatus
    source_type: str
    source_uri: str | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    frame_count: int | None = None
    duration: float | None = None
    message: str | None = None
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import cv2
import numpy as np
from sqlalchemy.orm import Session

from backend.app.models.camera import Camera
from backend.app.models.enums import CameraStatus, SourceType
from backend.app.video.exceptions import (
    SourceAlreadyStartedError,
    SourceFrameUnavailableError,
    SourceNotRunningError,
)
from backend.app.video.source import VideoMetadata, VideoSource, create_video_source, redact_rtsp_uri


@dataclass(slots=True)
class ManagedSourceState:
    camera_id: int
    source_type: SourceType
    source_uri: str
    metadata: VideoMetadata
    status: CameraStatus
    message: str | None = None
    source: VideoSource | None = None
    thread: threading.Thread | None = None
    stop_event: threading.Event | None = None
    latest_frame: np.ndarray | None = None
    lock: threading.Lock = field(default_factory=threading.Lock)


class VideoSourceManager:
    def __init__(
        self,
        session_factory: Callable[[], Session],
        reconnect_attempts: int = 3,
        reconnect_backoff_seconds: float = 1.0,
        storage_dir: Path | str = Path("storage"),
    ) -> None:
        self._session_factory = session_factory
        self._reconnect_attempts = reconnect_attempts
        self._reconnect_backoff_seconds = reconnect_backoff_seconds
        self._storage_dir = Path(storage_dir)
        self._logger = logging.getLogger(__name__)
        self._states: dict[int, ManagedSourceState] = {}
        self._lock = threading.Lock()

    def start(self, camera: Camera) -> ManagedSourceState:
        with self._lock:
            existing = self._states.get(camera.id)
            if existing is not None and existing.thread is not None and existing.thread.is_alive():
                raise SourceAlreadyStartedError(f"Camera {camera.id} is already started")

            source = create_video_source(camera)
            if not source.open():
                self._update_camera_status(camera.id, self._start_failure_status(camera))
                raise SourceNotRunningError(f"Failed to open source for camera {camera.id}")

            metadata = source.metadata()
            state = ManagedSourceState(
                camera_id=camera.id,
                source_type=camera.source_type,
                source_uri=self._redact_source_uri(camera),
                metadata=metadata,
                status=CameraStatus.CONNECTING,
                source=source,
                stop_event=threading.Event(),
            )
            self._states[camera.id] = state
            self._update_camera_status(camera.id, CameraStatus.CONNECTING)

            worker = threading.Thread(target=self._capture_loop, args=(state,), daemon=True)
            state.thread = worker
            worker.start()
            return state

    def stop(self, camera_id: int) -> ManagedSourceState:
        state = self._states.get(camera_id)
        if state is None:
            raise SourceNotRunningError(f"Camera {camera_id} is not running")

        if state.stop_event is not None:
            state.stop_event.set()

        if state.thread is not None and state.thread.is_alive():
            state.thread.join(timeout=5)

        if state.source is not None:
            state.source.release()

        state.status = CameraStatus.OFFLINE
        state.message = "Stopped"
        self._update_camera_status(camera_id, CameraStatus.OFFLINE)
        return state

    def stop_all(self) -> None:
        for camera_id in list(self._states):
            try:
                self.stop(camera_id)
            except SourceNotRunningError:
                continue

    def status(self, camera_id: int) -> ManagedSourceState:
        state = self._states.get(camera_id)
        if state is None:
            return ManagedSourceState(
                camera_id=camera_id,
                source_type=SourceType.VIDEO_FILE,
                source_uri="",
                metadata=VideoMetadata(source_type=SourceType.VIDEO_FILE, source_uri=""),
                status=CameraStatus.UNKNOWN,
                message="Source has not been started",
            )
        return state

    def metadata(self, camera_id: int, camera: Camera) -> ManagedSourceState:
        state = self._states.get(camera_id)
        if state is not None:
            return state

        metadata = VideoMetadata(source_type=camera.source_type, source_uri=self._redact_source_uri(camera))
        return ManagedSourceState(
            camera_id=camera_id,
            source_type=camera.source_type,
            source_uri=metadata.source_uri,
            metadata=metadata,
            status=CameraStatus.UNKNOWN,
            message="Source has not been started",
        )

    def snapshot(self, camera_id: int) -> bytes:
        state = self._states.get(camera_id)
        if state is None or state.latest_frame is None:
            raise SourceFrameUnavailableError(f"No frame is available for camera {camera_id}")

        success, encoded = cv2.imencode(".jpg", state.latest_frame)
        if not success:
            raise SourceFrameUnavailableError(f"Failed to encode snapshot for camera {camera_id}")
        return encoded.tobytes()

    def _capture_loop(self, state: ManagedSourceState) -> None:
        assert state.source is not None
        assert state.stop_event is not None

        source = state.source
        camera_id = state.camera_id
        reconnect_attempts = 0

        while not state.stop_event.is_set():
            success, frame = source.read()
            if success and frame is not None:
                with state.lock:
                    state.latest_frame = frame.copy()
                reconnect_attempts = 0
                if state.status != CameraStatus.ONLINE:
                    state.status = CameraStatus.ONLINE
                    self._update_camera_status(camera_id, CameraStatus.ONLINE)
                continue

            if state.source_type == SourceType.VIDEO_FILE:
                state.status = CameraStatus.OFFLINE
                state.message = "Video reached EOF"
                self._update_camera_status(camera_id, CameraStatus.OFFLINE)
                break

            reconnect_attempts += 1
            if reconnect_attempts > self._reconnect_attempts:
                state.status = CameraStatus.OFFLINE
                state.message = "Reconnect limit reached"
                self._update_camera_status(camera_id, CameraStatus.OFFLINE)
                break

            state.status = CameraStatus.RECONNECTING
            state.message = f"Reconnect attempt {reconnect_attempts}"
            self._update_camera_status(camera_id, CameraStatus.RECONNECTING)
            source.release()
            time.sleep(self._reconnect_backoff_seconds * reconnect_attempts)

            if not source.open():
                continue

            state.metadata = source.metadata()
            state.status = CameraStatus.ONLINE
            state.message = None
            self._update_camera_status(camera_id, CameraStatus.ONLINE)

        source.release()

    def _update_camera_status(self, camera_id: int, status: CameraStatus) -> None:
        with self._session_factory() as session:
            camera = session.get(Camera, camera_id)
            if camera is None:
                return
            if camera.status != status.value:
                camera.status = status.value
                session.commit()

    def _start_failure_status(self, camera: Camera) -> CameraStatus:
        if camera.source_type == SourceType.VIDEO_FILE:
            return CameraStatus.ERROR
        return CameraStatus.OFFLINE

    def _redact_source_uri(self, camera: Camera) -> str:
        if camera.source_type == SourceType.RTSP:
            return redact_rtsp_uri(camera.source_uri)
        return camera.source_uri
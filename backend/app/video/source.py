from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import cv2
import numpy as np

from backend.app.models.camera import Camera
from backend.app.models.enums import SourceType
from backend.app.video.exceptions import UnsupportedSourceTypeError

PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass(slots=True)
class VideoMetadata:
    source_type: SourceType
    source_uri: str
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    frame_count: int | None = None
    duration: float | None = None


class VideoSource(ABC):
    @abstractmethod
    def open(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def read(self) -> tuple[bool, np.ndarray | None]:
        raise NotImplementedError

    @abstractmethod
    def is_opened(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def release(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> VideoMetadata:
        raise NotImplementedError


class OpenCVVideoSource(VideoSource):
    def __init__(self, source_input: Any, source_type: SourceType, source_uri: str) -> None:
        self._source_input = source_input
        self._source_type = source_type
        self._source_uri = source_uri
        self._capture: cv2.VideoCapture | None = None
        self._metadata = VideoMetadata(source_type=source_type, source_uri=source_uri)

    def open(self) -> bool:
        if self._capture is not None and self._capture.isOpened():
            return True

        capture = cv2.VideoCapture(self._source_input)
        if not capture.isOpened():
            capture.release()
            self._capture = None
            return False

        self._capture = capture
        self._metadata = self._capture_metadata()
        return True

    def read(self) -> tuple[bool, np.ndarray | None]:
        if not self.is_opened() or self._capture is None:
            return False, None

        success, frame = self._capture.read()
        if not success or frame is None:
            return False, None
        return True, frame

    def is_opened(self) -> bool:
        return self._capture is not None and self._capture.isOpened()

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    def metadata(self) -> VideoMetadata:
        if self.is_opened():
            self._metadata = self._capture_metadata()
        return self._metadata

    def _capture_metadata(self) -> VideoMetadata:
        assert self._capture is not None
        width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0) or None
        height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0) or None
        fps = float(self._capture.get(cv2.CAP_PROP_FPS) or 0.0) or None
        frame_count_value = int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0) or None
        duration = None
        if fps and frame_count_value:
            duration = frame_count_value / fps

        return VideoMetadata(
            source_type=self._source_type,
            source_uri=self._source_uri,
            width=width,
            height=height,
            fps=fps,
            frame_count=frame_count_value,
            duration=duration,
        )


class LocalVideoSource(OpenCVVideoSource):
    def __init__(self, source_uri: str) -> None:
        path = Path(source_uri)
        resolved_path = path if path.is_absolute() else PROJECT_ROOT / path
        self.resolved_path = resolved_path
        super().__init__(str(resolved_path), SourceType.VIDEO_FILE, source_uri)


class WebcamSource(OpenCVVideoSource):
    def __init__(self, source_uri: str) -> None:
        index = int(source_uri)
        if index < 0:
            raise ValueError("Webcam index must be zero or positive")
        self.index = index
        super().__init__(index, SourceType.WEBCAM, source_uri)


class RTSPSource(OpenCVVideoSource):
    def __init__(self, source_uri: str) -> None:
        self.redacted_uri = redact_rtsp_uri(source_uri)
        super().__init__(source_uri, SourceType.RTSP, source_uri)


def create_video_source(camera: Camera) -> VideoSource:
    if camera.source_type == SourceType.VIDEO_FILE:
        resolved_path = Path(camera.source_uri)
        if not resolved_path.is_absolute():
            resolved_path = PROJECT_ROOT / resolved_path
        if not resolved_path.exists():
            raise FileNotFoundError(f"Video file does not exist: {camera.source_uri}")
        return LocalVideoSource(camera.source_uri)

    if camera.source_type == SourceType.WEBCAM:
        try:
            return WebcamSource(camera.source_uri)
        except ValueError as exc:
            raise ValueError(f"Invalid webcam source_uri: {camera.source_uri}") from exc

    if camera.source_type == SourceType.RTSP:
        return RTSPSource(camera.source_uri)

    raise UnsupportedSourceTypeError(f"Unsupported source_type: {camera.source_type}")


def redact_rtsp_uri(source_uri: str) -> str:
    parsed = urlsplit(source_uri)
    if parsed.username is None and parsed.password is None:
        return source_uri

    netloc = parsed.hostname or ""
    if parsed.port is not None:
        netloc = f"{netloc}:{parsed.port}"
    if parsed.username:
        netloc = f"***@{netloc}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
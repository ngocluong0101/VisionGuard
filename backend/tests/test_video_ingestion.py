from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np

from backend.app.models.enums import SourceType
from backend.app.video.exceptions import UnsupportedSourceTypeError
from backend.app.video.source import LocalVideoSource, WebcamSource, create_video_source


def _write_sample_mp4(path: Path, frame_count: int = 3, width: int = 64, height: int = 48, fps: float = 5.0) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    assert writer.isOpened()

    for index in range(frame_count):
        frame = np.full((height, width, 3), 30 + index * 20, dtype=np.uint8)
        writer.write(frame)

    writer.release()


class FakeVideoCapture:
    def __init__(self, source_input, frames: list[np.ndarray] | None = None, opened: bool = True) -> None:
        self.source_input = source_input
        self.frames = frames or []
        self.opened = opened
        self.width = 64
        self.height = 48
        self.fps = 15.0

    def isOpened(self) -> bool:
        return self.opened

    def read(self):
        if not self.opened or not self.frames:
            return False, None
        return True, self.frames.pop(0)

    def release(self) -> None:
        self.opened = False

    def get(self, prop_id):
        if prop_id == cv2.CAP_PROP_FRAME_WIDTH:
            return self.width
        if prop_id == cv2.CAP_PROP_FRAME_HEIGHT:
            return self.height
        if prop_id == cv2.CAP_PROP_FPS:
            return self.fps
        if prop_id == cv2.CAP_PROP_FRAME_COUNT:
            return len(self.frames)
        return 0


def test_video_source_factory_and_local_mp4_source(tmp_path: Path) -> None:
    video_path = tmp_path / "sample.mp4"
    _write_sample_mp4(video_path)

    source = create_video_source(SimpleNamespace(source_type=SourceType.VIDEO_FILE, source_uri=str(video_path)))
    assert isinstance(source, LocalVideoSource)
    assert source.open() is True

    metadata = source.metadata()
    assert metadata.width == 64
    assert metadata.height == 48
    assert metadata.fps is not None and metadata.fps > 0

    success, frame = source.read()
    assert success is True
    assert frame is not None
    assert frame.shape[0] == 48
    assert frame.shape[1] == 64

    source.release()
    assert source.is_opened() is False


def test_webcam_index_parsing_and_invalid_source_type(monkeypatch) -> None:
    fake_frame = np.full((48, 64, 3), 120, dtype=np.uint8)

    def fake_video_capture(source_input):
        return FakeVideoCapture(source_input, frames=[fake_frame.copy()])

    monkeypatch.setattr("backend.app.video.source.cv2.VideoCapture", fake_video_capture)

    source = create_video_source(SimpleNamespace(source_type=SourceType.WEBCAM, source_uri="0"))
    assert isinstance(source, WebcamSource)
    assert source.open() is True
    success, frame = source.read()
    assert success is True
    assert frame is not None
    source.release()

    try:
        create_video_source(SimpleNamespace(source_type=SourceType.WEBCAM, source_uri="not-an-index"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid webcam index to raise ValueError")

    try:
        create_video_source(SimpleNamespace(source_type="BAD", source_uri="x"))
    except UnsupportedSourceTypeError:
        pass
    else:
        raise AssertionError("Expected invalid source type to raise UnsupportedSourceTypeError")


def test_rtsp_source_factory_uses_same_interface(monkeypatch) -> None:
    fake_frame = np.full((48, 64, 3), 200, dtype=np.uint8)

    def fake_video_capture(source_input):
        return FakeVideoCapture(source_input, frames=[fake_frame.copy()])

    monkeypatch.setattr("backend.app.video.source.cv2.VideoCapture", fake_video_capture)

    source = create_video_source(SimpleNamespace(source_type=SourceType.RTSP, source_uri="rtsp://user:secret@localhost:8554/live"))
    assert source.open() is True
    success, frame = source.read()
    assert success is True
    assert frame is not None
    source.release()
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def _write_sample_mp4(path: Path, frame_count: int = 4, width: int = 80, height: int = 60, fps: float = 5.0) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(path), fourcc, fps, (width, height))
    assert writer.isOpened()

    for index in range(frame_count):
        frame = np.full((height, width, 3), 40 + index * 20, dtype=np.uint8)
        cv2.putText(frame, str(index), (8, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        writer.write(frame)

    writer.release()


def test_upload_mp4_start_metadata_snapshot_and_stop(client, tmp_path: Path) -> None:
    source_file = tmp_path / "source.mp4"
    _write_sample_mp4(source_file)

    with source_file.open("rb") as handle:
        upload_response = client.post(
            "/api/v1/video-sources/upload",
            files={"file": ("test-upload.mp4", handle, "video/mp4")},
        )

    assert upload_response.status_code == 201
    upload_payload = upload_response.json()
    assert upload_payload["source_type"] == "VIDEO_FILE"
    assert upload_payload["storage_path"].startswith("storage/uploads/")

    camera_response = client.post(
        "/api/v1/cameras",
        json={
            "name": "Uploaded Parking Video",
            "location_id": None,
            "source_type": "VIDEO_FILE",
            "source_uri": upload_payload["storage_path"],
            "status": "UNKNOWN",
            "description": "Phase 04 MP4 test source",
        },
    )
    assert camera_response.status_code == 201
    camera_id = camera_response.json()["id"]

    start_response = client.post(f"/api/v1/cameras/{camera_id}/start")
    assert start_response.status_code == 200
    assert start_response.json()["camera_id"] == camera_id

    metadata_response = client.get(f"/api/v1/cameras/{camera_id}/metadata")
    assert metadata_response.status_code == 200
    metadata_payload = metadata_response.json()
    assert metadata_payload["camera_id"] == camera_id
    assert metadata_payload["source_type"] == "VIDEO_FILE"
    assert metadata_payload["width"] == 80
    assert metadata_payload["height"] == 60
    assert metadata_payload["fps"] is not None

    snapshot_response = client.get(f"/api/v1/cameras/{camera_id}/snapshot")
    assert snapshot_response.status_code == 200
    assert snapshot_response.headers["content-type"] == "image/jpeg"
    assert len(snapshot_response.content) > 0

    status_response = client.get(f"/api/v1/cameras/{camera_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["status"] in {"ONLINE", "OFFLINE", "CONNECTING"}

    stop_response = client.post(f"/api/v1/cameras/{camera_id}/stop")
    assert stop_response.status_code == 200
    assert stop_response.json()["status"] == "OFFLINE"


def test_upload_validation_and_camera_error_cases(client) -> None:
    invalid_upload = client.post(
        "/api/v1/video-sources/upload",
        files={"file": ("not-a-video.txt", b"hello", "text/plain")},
    )
    assert invalid_upload.status_code == 415

    assert client.post("/api/v1/cameras/999999/start").status_code == 404
    assert client.post("/api/v1/cameras/999999/stop").status_code == 404
    assert client.get("/api/v1/cameras/999999/status").status_code == 404
    assert client.get("/api/v1/cameras/999999/metadata").status_code == 404
    assert client.get("/api/v1/cameras/999999/snapshot").status_code == 404
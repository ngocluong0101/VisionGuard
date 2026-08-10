from datetime import datetime, timezone


def test_location_camera_zone_event_recording_crud_and_foreign_keys(client) -> None:
    location_response = client.post(
        "/api/v1/locations",
        json={"name": "Head Office", "description": "Main site"},
    )
    assert location_response.status_code == 201
    location_id = location_response.json()["id"]

    location_detail_response = client.get(f"/api/v1/locations/{location_id}")
    assert location_detail_response.status_code == 200
    assert location_detail_response.json()["name"] == "Head Office"

    location_patch_response = client.patch(
        f"/api/v1/locations/{location_id}",
        json={"description": "Updated site"},
    )
    assert location_patch_response.status_code == 200
    assert location_patch_response.json()["description"] == "Updated site"

    camera_response = client.post(
        "/api/v1/cameras",
        json={
            "name": "Lobby Camera",
            "location_id": location_id,
            "source_type": "WEBCAM",
            "source_uri": "0",
            "status": "UNKNOWN",
            "description": "Entrance monitoring",
        },
    )
    assert camera_response.status_code == 201
    camera_id = camera_response.json()["id"]

    zone_response = client.post(
        "/api/v1/zones",
        json={
            "camera_id": camera_id,
            "name": "Lobby Restricted Zone",
            "zone_type": "RESTRICTED",
            "coordinates": [[0.1, 0.2], [0.8, 0.2], [0.8, 0.9], [0.1, 0.9]],
            "enabled": True,
        },
    )
    assert zone_response.status_code == 201
    zone_id = zone_response.json()["id"]

    event_response = client.post(
        "/api/v1/events",
        json={
            "camera_id": camera_id,
            "event_type": "INTRUSION",
            "severity": "WARNING",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "track_id": 7,
            "object_class": "person",
            "confidence": 0.91,
            "snapshot_path": None,
            "video_path": None,
            "metadata": {"zone_id": zone_id},
        },
    )
    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    recording_response = client.post(
        "/api/v1/recordings",
        json={
            "camera_id": camera_id,
            "event_id": event_id,
            "file_path": "storage/recordings/event-0001.mp4",
            "start_time": datetime.now(timezone.utc).isoformat(),
            "end_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert recording_response.status_code == 201
    recording_id = recording_response.json()["id"]

    assert client.get("/api/v1/locations").status_code == 200
    assert client.get("/api/v1/cameras").status_code == 200
    assert client.get("/api/v1/zones").status_code == 200
    assert client.get("/api/v1/events").status_code == 200
    assert client.get("/api/v1/recordings").status_code == 200

    location_delete_response = client.delete(f"/api/v1/locations/{location_id}")
    assert location_delete_response.status_code == 204

    camera_after_location_delete = client.get(f"/api/v1/cameras/{camera_id}")
    assert camera_after_location_delete.status_code == 200
    assert camera_after_location_delete.json()["location_id"] is None

    camera_delete_response = client.delete(f"/api/v1/cameras/{camera_id}")
    assert camera_delete_response.status_code == 204

    zone_after_camera_delete = client.get(f"/api/v1/zones/{zone_id}")
    assert zone_after_camera_delete.status_code == 200
    assert zone_after_camera_delete.json()["camera_id"] is None

    event_after_camera_delete = client.get(f"/api/v1/events/{event_id}")
    assert event_after_camera_delete.status_code == 200
    assert event_after_camera_delete.json()["camera_id"] is None

    recording_after_camera_delete = client.get(f"/api/v1/recordings/{recording_id}")
    assert recording_after_camera_delete.status_code == 200
    assert recording_after_camera_delete.json()["camera_id"] is None

    assert client.delete(f"/api/v1/zones/{zone_id}").status_code == 204
    assert client.delete(f"/api/v1/events/{event_id}").status_code == 204
    assert client.delete(f"/api/v1/recordings/{recording_id}").status_code == 204


def test_validation_and_404_behavior(client) -> None:
    invalid_camera_response = client.post(
        "/api/v1/cameras",
        json={
            "name": "Incomplete Camera",
            "location_id": 1,
            "source_type": "RTSP",
        },
    )
    assert invalid_camera_response.status_code == 422

    assert client.get("/api/v1/locations/99999").status_code == 404
    assert client.get("/api/v1/cameras/99999").status_code == 404
    assert client.get("/api/v1/zones/99999").status_code == 404
    assert client.get("/api/v1/events/99999").status_code == 404
    assert client.get("/api/v1/recordings/99999").status_code == 404
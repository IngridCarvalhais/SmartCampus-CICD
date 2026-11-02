import pytest
from fastapi.testclient import TestClient


def booking_payload(
    room_id: int,
    start: str = "09:00",
    end: str = "10:00",
) -> dict[str, object]:
    return {
        "aula_id": room_id,
        "usuario": "estudiante",
        "fecha": "2026-11-10",
        "hora_inicio": start,
        "hora_fin": end,
    }


def test_create_and_list_bookings(
    client: TestClient,
    room_id: int,
) -> None:
    created = client.post("/bookings", json=booking_payload(room_id))

    assert created.status_code == 201
    assert created.json()["aula_id"] == room_id
    assert client.get("/bookings").json() == [created.json()]


def test_create_booking_rejects_missing_room(client: TestClient) -> None:
    response = client.post("/bookings", json=booking_payload(999))

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("start", "end"),
    [("10:00", "10:00"), ("11:00", "10:00")],
)
def test_create_booking_rejects_invalid_schedule(
    client: TestClient,
    room_id: int,
    start: str,
    end: str,
) -> None:
    response = client.post(
        "/bookings",
        json=booking_payload(room_id, start, end),
    )

    assert response.status_code == 422


def test_create_booking_rejects_overlap(
    client: TestClient,
    room_id: int,
) -> None:
    first = client.post("/bookings", json=booking_payload(room_id))
    overlapping = client.post(
        "/bookings",
        json=booking_payload(room_id, "09:30", "10:30"),
    )

    assert first.status_code == 201
    assert overlapping.status_code == 409


def test_create_booking_allows_consecutive_schedule(
    client: TestClient,
    room_id: int,
) -> None:
    first = client.post("/bookings", json=booking_payload(room_id))
    consecutive = client.post(
        "/bookings",
        json=booking_payload(room_id, "10:00", "11:00"),
    )

    assert first.status_code == 201
    assert consecutive.status_code == 201


def test_delete_booking(client: TestClient, room_id: int) -> None:
    created = client.post("/bookings", json=booking_payload(room_id))
    booking_id = created.json()["id"]

    deleted = client.delete(f"/bookings/{booking_id}")

    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get("/bookings").json() == []


def test_delete_missing_booking_returns_404(client: TestClient) -> None:
    response = client.delete("/bookings/999")

    assert response.status_code == 404

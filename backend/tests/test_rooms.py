import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("capacity", [0, -1])
def test_create_room_rejects_non_positive_capacity(
    client: TestClient,
    capacity: int,
) -> None:
    response = client.post(
        "/rooms",
        json={
            "nombre": "Aula no válida",
            "edificio": "Edificio A",
            "capacidad": capacity,
            "equipamiento": [],
        },
    )

    assert response.status_code == 422


def test_create_and_list_rooms(client: TestClient) -> None:
    payload = {
        "nombre": "Aula 101",
        "edificio": "Edificio A",
        "capacidad": 30,
        "equipamiento": ["proyector"],
    }

    created = client.post("/rooms", json=payload)

    assert created.status_code == 201
    assert created.json()["nombre"] == payload["nombre"]
    assert client.get("/rooms").json() == [created.json()]


def test_delete_room(client: TestClient, room_id: int) -> None:
    response = client.delete(f"/rooms/{room_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/rooms/{room_id}").status_code == 404


def test_delete_room_with_bookings_returns_conflict(
    client: TestClient,
    room_id: int,
) -> None:
    booking = client.post(
        "/bookings",
        json={
            "aula_id": room_id,
            "usuario": "estudiante",
            "fecha": "2026-11-10",
            "hora_inicio": "09:00",
            "hora_fin": "10:00",
        },
    )
    assert booking.status_code == 201

    response = client.delete(f"/rooms/{room_id}")

    assert response.status_code == 409
    assert client.get(f"/rooms/{room_id}").status_code == 200
    assert client.get("/bookings").json() == [booking.json()]


def test_delete_missing_room_returns_404(client: TestClient) -> None:
    response = client.delete("/rooms/999")

    assert response.status_code == 404

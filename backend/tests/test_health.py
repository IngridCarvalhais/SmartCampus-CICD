from datetime import date, time

from fastapi.testclient import TestClient

from app.db.connection import SessionLocal
from app.models import Booking, Room


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_rooms_returns_empty_list(client: TestClient) -> None:
    response = client.get("/rooms")

    assert response.status_code == 200
    assert response.json() == []


def test_list_rooms_returns_rooms(client: TestClient) -> None:
    with SessionLocal() as database:
        room = Room(
            nombre="Aula 103",
            edificio="Edificio A",
            capacidad=25,
            equipamiento=["pizarra"],
        )
        database.add(room)
        database.commit()
        room_id = room.id

    response = client.get("/rooms")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": room_id,
            "nombre": "Aula 103",
            "edificio": "Edificio A",
            "capacidad": 25,
            "equipamiento": ["pizarra"],
        }
    ]


def test_get_room_returns_room(client: TestClient) -> None:
    with SessionLocal() as database:
        room = Room(
            nombre="Aula 101",
            edificio="Edificio A",
            capacidad=30,
            equipamiento=["proyector", "pizarra"],
        )
        database.add(room)
        database.commit()
        room_id = room.id

    response = client.get(f"/rooms/{room_id}")

    assert response.status_code == 200
    assert response.json() == {
        "id": room_id,
        "nombre": "Aula 101",
        "edificio": "Edificio A",
        "capacidad": 30,
        "equipamiento": ["proyector", "pizarra"],
    }


def test_get_missing_room_returns_404(client: TestClient) -> None:
    response = client.get("/rooms/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Aula no encontrada"}


def test_list_bookings_returns_booking(client: TestClient) -> None:
    with SessionLocal() as database:
        room = Room(
            nombre="Aula 202",
            edificio="Edificio B",
            capacidad=20,
            equipamiento=["pantalla"],
        )
        database.add(room)
        database.flush()
        booking = Booking(
            aula_id=room.id,
            usuario="estudiante",
            fecha=date(2026, 11, 1),
            hora_inicio=time(9, 0),
            hora_fin=time(10, 0),
        )
        database.add(booking)
        database.commit()
        booking_id = booking.id
        room_id = room.id

    response = client.get("/bookings")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": booking_id,
            "aula_id": room_id,
            "usuario": "estudiante",
            "fecha": "2026-11-01",
            "hora_inicio": "09:00:00",
            "hora_fin": "10:00:00",
        }
    ]

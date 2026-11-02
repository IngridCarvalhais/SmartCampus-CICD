from datetime import date, time

import pytest
from pydantic import ValidationError

from app.schemas.booking import BookingCreate
from app.schemas.room import RoomCreate


@pytest.mark.parametrize("capacity", [0, -1])
def test_room_schema_rejects_non_positive_capacity(capacity: int) -> None:
    with pytest.raises(ValidationError):
        RoomCreate(
            nombre="Aula",
            edificio="Edificio A",
            capacidad=capacity,
        )


@pytest.mark.parametrize(
    ("start", "end"),
    [(time(10), time(10)), (time(11), time(10))],
)
def test_booking_schema_rejects_invalid_schedule(
    start: time,
    end: time,
) -> None:
    with pytest.raises(ValidationError):
        BookingCreate(
            aula_id=1,
            usuario="estudiante",
            fecha=date(2026, 11, 10),
            hora_inicio=start,
            hora_fin=end,
        )

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.booking import Booking
from app.models.room import Room
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter()


@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(database: Session = Depends(get_db)) -> list[Booking]:
    return list(database.scalars(select(Booking).order_by(Booking.id)).all())


@router.post(
    "/bookings",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_data: BookingCreate,
    database: Session = Depends(get_db),
) -> Booking:
    room = database.get(Room, booking_data.aula_id)

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aula no encontrada",
        )

    overlapping = database.scalar(
        select(Booking).where(
            Booking.aula_id == booking_data.aula_id,
            Booking.fecha == booking_data.fecha,
            Booking.hora_inicio < booking_data.hora_fin,
            Booking.hora_fin > booking_data.hora_inicio,
        )
    )

    if overlapping is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El aula ya está reservada en ese horario",
        )

    booking = Booking(**booking_data.model_dump())

    database.add(booking)
    database.commit()
    database.refresh(booking)

    return booking


@router.delete(
    "/bookings/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_booking(
    booking_id: Annotated[int, Path(alias="id")],
    database: Session = Depends(get_db),
) -> None:
    booking = database.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )

    database.delete(booking)
    database.commit()

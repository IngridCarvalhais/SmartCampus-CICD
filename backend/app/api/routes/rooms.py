from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.booking import Booking
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomResponse

router = APIRouter()


@router.get("/rooms", response_model=list[RoomResponse])
def list_rooms(database: Session = Depends(get_db)) -> list[Room]:
    return list(database.scalars(select(Room).order_by(Room.id)).all())


@router.get("/rooms/{id}", response_model=RoomResponse)
def get_room(
    room_id: Annotated[int, Path(alias="id")],
    database: Session = Depends(get_db),
) -> Room:
    room = database.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
    return room


@router.post(
    "/rooms",
    response_model=RoomResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_room(
    room_data: RoomCreate,
    database: Session = Depends(get_db),
) -> Room:
    room = Room(**room_data.model_dump())

    database.add(room)
    database.commit()
    database.refresh(room)

    return room


@router.delete(
    "/rooms/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_room(
    room_id: Annotated[int, Path(alias="id")],
    database: Session = Depends(get_db),
) -> None:
    room = database.get(Room, room_id)

    if room is None:
        raise HTTPException(
            status_code=404,
            detail="Aula no encontrada",
        )

    has_bookings = database.scalar(
        select(Booking.id).where(Booking.aula_id == room_id).limit(1)
    )
    if has_bookings is not None:
        raise HTTPException(
            status_code=409,
            detail="No se puede eliminar un aula con reservas asociadas",
        )

    database.delete(room)
    database.commit()

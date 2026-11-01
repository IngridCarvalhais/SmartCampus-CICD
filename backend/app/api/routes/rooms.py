from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.room import Room
from app.schemas.room import RoomResponse

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
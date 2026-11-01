from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingResponse

router = APIRouter()


@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(database: Session = Depends(get_db)) -> list[Booking]:
    return list(database.scalars(select(Booking).order_by(Booking.id)).all())
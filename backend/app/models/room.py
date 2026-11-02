from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    edificio: Mapped[str] = mapped_column(String(150), nullable=False)
    capacidad: Mapped[int] = mapped_column(Integer, nullable=False)
    equipamiento: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

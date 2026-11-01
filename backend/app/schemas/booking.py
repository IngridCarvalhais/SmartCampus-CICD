from datetime import date, time

from pydantic import BaseModel, ConfigDict


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aula_id: int
    usuario: str
    fecha: date
    hora_inicio: time
    hora_fin: time
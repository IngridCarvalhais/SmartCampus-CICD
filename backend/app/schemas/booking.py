from datetime import date, time
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingCreate(BaseModel):
    aula_id: int = Field(gt=0)
    usuario: str = Field(min_length=1, max_length=150)
    fecha: date
    hora_inicio: time
    hora_fin: time

    @model_validator(mode="after")
    def validate_schedule(self) -> Self:
        if self.hora_inicio >= self.hora_fin:
            raise ValueError("La hora de inicio debe ser anterior a la hora de fin")
        return self


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    aula_id: int
    usuario: str
    fecha: date
    hora_inicio: time
    hora_fin: time

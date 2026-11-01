from pydantic import BaseModel, ConfigDict, Field


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    edificio: str
    capacidad: int = Field(ge=0)
    equipamiento: list[str]
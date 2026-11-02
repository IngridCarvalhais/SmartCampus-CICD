from pydantic import BaseModel, ConfigDict, Field


class RoomCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    edificio: str = Field(min_length=1, max_length=150)
    capacidad: int = Field(gt=0)
    equipamiento: list[str] = Field(default_factory=list)


class RoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    edificio: str
    capacidad: int = Field(gt=0)
    equipamiento: list[str]

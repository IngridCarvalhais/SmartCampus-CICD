from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.routes.bookings import router as bookings_router
from app.api.routes.health import router as health_router
from app.api.routes.rooms import router as rooms_router
from app.db.connection import create_tables


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_tables()
    yield


app = FastAPI(title="SmartCampus API", lifespan=lifespan)
app.include_router(health_router)
app.include_router(rooms_router)
app.include_router(bookings_router)
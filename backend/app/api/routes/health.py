from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.connection import get_db

router = APIRouter()


@router.get("/health")
def health(database: Session = Depends(get_db)) -> dict[str, str]:
    database.execute(text("SELECT 1"))
    return {"status": "ok"}

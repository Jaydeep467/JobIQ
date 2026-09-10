from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db


router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "jobiq-api",
    }


@router.get("/db-health")
def db_health(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    value = result.scalar()

    return {
        "status": "healthy",
        "database": "connected",
        "result": value,
    }
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import get_periods_for_company

router = APIRouter(prefix="/periods", tags=["periods"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def list_periods(db: Session = Depends(get_db)):
    company = get_or_create_company(db)
    periods = get_periods_for_company(db, company.id)
    return [
        {
            "id": p.id,
            "label": p.label,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "period_type": p.period_type,
        }
        for p in periods
    ]
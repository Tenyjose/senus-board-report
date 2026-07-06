from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.customer_metrics import CustomerMetrics
from app.api.metrics import build_period_metrics
from app.services.insights import generate_period_insights

router = APIRouter(prefix="/periods", tags=["insights"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{period_id}/insights")
def get_period_insights(period_id: int, db: Session = Depends(get_db)):
    metrics = build_period_metrics(db, period_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail=f"No period found with id {period_id}")

    customer_metrics = db.query(CustomerMetrics).filter_by(period_id=period_id).first()
    commercial_context = {
        "notable_commercial_events": customer_metrics.notable_commercial_events if customer_metrics else [],
        "new_deals_closed_value": customer_metrics.new_deals_closed_value if customer_metrics else None,
        "open_pipeline_value": customer_metrics.open_pipeline_value if customer_metrics else None,
    }

    commentary = generate_period_insights(metrics, commercial_context)
    return {"period": metrics["period"], "commentary": commentary}
from sqlalchemy.orm import Session

from app.models.reporting_period import ReportingPeriod
from app.models.income_statement import IncomeStatement


def get_periods_for_company(session: Session, company_id: int) -> list[ReportingPeriod]:
    """Return all reporting periods for a company, oldest first."""
    return (
        session.query(ReportingPeriod)
        .filter_by(company_id=company_id)
        .order_by(ReportingPeriod.start_date)
        .all()
    )


def calculate_revenue_growth_pct(current: IncomeStatement, prior: IncomeStatement) -> float | None:
    """
    Percentage change in revenue between two periods.
    Returns None if prior revenue is zero or missing, since growth
    from zero is undefined, not a real number.
    """
    if not prior.revenue or prior.revenue == 0:
        return None
    if current.revenue is None:
        return None

    growth = (current.revenue - prior.revenue) / prior.revenue * 100
    return round(float(growth), 2)
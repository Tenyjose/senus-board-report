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


def calculate_ebitda(operating_result, depreciation, amortisation=0) -> float | None:
    if operating_result is None:
        return None

    dep = depreciation or 0
    amort = amortisation or 0
    return round(float(operating_result) + float(dep) + float(amort), 2)


def calculate_gross_margin_pct(gross_profit, revenue) -> float | None:
    if not revenue or revenue == 0 or gross_profit is None:
        return None
    return round(float(gross_profit) / float(revenue) * 100, 2)


def calculate_operating_margin_pct(operating_result, revenue) -> float | None:
    if not revenue or revenue == 0 or operating_result is None:
        return None
    return round(float(operating_result) / float(revenue) * 100, 2)


def calculate_ebitda_margin_pct(ebitda, revenue) -> float | None:
    if not revenue or revenue == 0 or ebitda is None:
        return None
    return round(float(ebitda) / float(revenue) * 100, 2)
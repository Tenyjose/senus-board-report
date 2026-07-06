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



def calculate_working_capital(net_current_assets) -> float | None:
    if net_current_assets is None:
        return None
    return float(net_current_assets)


def calculate_free_cash_flow(operating_cf, investing_cf) -> float | None:
    if operating_cf is None or investing_cf is None:
        return None
    return round(float(operating_cf) + float(investing_cf), 2)


def calculate_ebitda_to_fcf_bridge(ebitda, operating_cf, investing_cf) -> dict | None:
    if ebitda is None or operating_cf is None or investing_cf is None:
        return None

    working_capital_and_other_adjustments = round(float(operating_cf) - float(ebitda), 2)
    free_cash_flow = calculate_free_cash_flow(operating_cf, investing_cf)

    return {
        "ebitda": round(float(ebitda), 2),
        "working_capital_and_other_adjustments": working_capital_and_other_adjustments,
        "operating_cash_flow": round(float(operating_cf), 2),
        "capex_and_investing": round(float(investing_cf), 2),
        "free_cash_flow": free_cash_flow,
    }


def calculate_cash_runway_months(cash_at_end, operating_cf, period_start_date, period_end_date) -> float | None:
    if cash_at_end is None or operating_cf is None:
        return None
    if float(operating_cf) >= 0:
        return None

    days_in_period = (period_end_date - period_start_date).days
    months_in_period = days_in_period / 30.44  # average days per month

    if months_in_period <= 0:
        return None

    monthly_burn = abs(float(operating_cf)) / months_in_period
    if monthly_burn == 0:
        return None

    return round(float(cash_at_end) / monthly_burn, 1)


def calculate_capital_employed(fixed_assets, net_current_assets) -> float | None:
    if fixed_assets is None or net_current_assets is None:
        return None
    return round(float(fixed_assets) + float(net_current_assets), 2)


def calculate_roce_pct(operating_result, capital_employed) -> float | None:
    if operating_result is None or not capital_employed or capital_employed == 0:
        return None
    return round(float(operating_result) / float(capital_employed) * 100, 2)
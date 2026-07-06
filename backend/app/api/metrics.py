from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.reporting_period import ReportingPeriod
from app.models.income_statement import IncomeStatement
from app.models.balance_sheet import BalanceSheet
from app.models.cash_flow import CashFlow
from app.services.metrics import (
    calculate_revenue_growth_pct,
    calculate_ebitda,
    calculate_gross_margin_pct,
    calculate_operating_margin_pct,
    calculate_ebitda_margin_pct,
    calculate_working_capital,
    calculate_ebitda_to_fcf_bridge,
    calculate_cash_runway_months,
    calculate_capital_employed,
    calculate_roce_pct,
    calculate_dscr,
)

router = APIRouter(prefix="/periods", tags=["metrics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_prior_period(db: Session, period: ReportingPeriod) -> ReportingPeriod | None:
    return (
        db.query(ReportingPeriod)
        .filter(
            ReportingPeriod.company_id == period.company_id,
            ReportingPeriod.start_date < period.start_date,
        )
        .order_by(ReportingPeriod.start_date.desc())
        .first()
    )


def build_period_metrics(db: Session, period_id: int) -> dict | None:
    """
    The actual metrics-calculation logic, kept separate from the route
    itself so other parts of the app (like the insights endpoint) can
    reuse it without making a second HTTP call to our own API.
    """
    period = db.query(ReportingPeriod).filter_by(id=period_id).first()
    if period is None:
        return None

    income = db.query(IncomeStatement).filter_by(period_id=period.id).first()
    balance = db.query(BalanceSheet).filter_by(period_id=period.id).first()
    cash = db.query(CashFlow).filter_by(period_id=period.id).first()

    prior_period = get_prior_period(db, period)
    prior_income = (
        db.query(IncomeStatement).filter_by(period_id=prior_period.id).first()
        if prior_period else None
    )

    ebitda = calculate_ebitda(income.operating_loss, cash.depreciation) if income and cash else None
    capital_employed = (
        calculate_capital_employed(balance.fixed_assets, balance.net_current_assets)
        if balance else None
    )

    return {
        "period": {
            "id": period.id,
            "label": period.label,
            "start_date": period.start_date,
            "end_date": period.end_date,
            "period_type": period.period_type,
        },
        "compared_to": prior_period.label if prior_period else None,
        "growth_and_revenue": {
            "revenue": income.revenue if income else None,
            "revenue_growth_pct": (
                calculate_revenue_growth_pct(income, prior_income)
                if income and prior_income else None
            ),
        },
        "profitability": {
            "gross_margin_pct": calculate_gross_margin_pct(income.gross_profit, income.revenue) if income else None,
            "operating_margin_pct": calculate_operating_margin_pct(income.operating_loss, income.revenue) if income else None,
            "ebitda": ebitda,
            "ebitda_margin_pct": calculate_ebitda_margin_pct(ebitda, income.revenue) if income else None,
        },
        "cash_and_liquidity": {
            "working_capital": calculate_working_capital(balance.net_current_assets) if balance else None,
            "ebitda_to_fcf_bridge": (
                calculate_ebitda_to_fcf_bridge(ebitda, cash.operating_cf, cash.investing_cf)
                if cash else None
            ),
            "cash_runway_months": (
                calculate_cash_runway_months(cash.cash_at_end, cash.operating_cf, period.start_date, period.end_date)
                if cash else None
            ),
        },
        "solvency_and_leverage": {
            "dscr": (
                calculate_dscr(ebitda, income.interest_expense, balance.principal_due_within_one_year)
                if income and balance else None
            ),
        },
        "returns": {
            "capital_employed": capital_employed,
            "roce_pct": (
                calculate_roce_pct(income.operating_loss, capital_employed)
                if income else None
            ),
        },
    }


@router.get("/{period_id}/metrics")
def get_period_metrics(period_id: int, db: Session = Depends(get_db)):
    metrics = build_period_metrics(db, period_id)
    if metrics is None:
        raise HTTPException(status_code=404, detail=f"No period found with id {period_id}")
    return metrics
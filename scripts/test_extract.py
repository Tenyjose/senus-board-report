import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import (
    get_periods_for_company,
    calculate_ebitda,
    calculate_gross_margin_pct,
    calculate_operating_margin_pct,
    calculate_ebitda_margin_pct,
)
from app.models.income_statement import IncomeStatement
from app.models.cash_flow import CashFlow

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = get_periods_for_company(session, company.id)

    for p in periods:
        income = session.query(IncomeStatement).filter_by(period_id=p.id).first()
        cash = session.query(CashFlow).filter_by(period_id=p.id).first()

        if income is None:
            print(f"{p.label}: skipping, no income statement")
            continue

        depreciation = cash.depreciation if cash else None
        ebitda = calculate_ebitda(income.operating_loss, depreciation)

        gross_margin = calculate_gross_margin_pct(income.gross_profit, income.revenue)
        operating_margin = calculate_operating_margin_pct(income.operating_loss, income.revenue)
        ebitda_margin = calculate_ebitda_margin_pct(ebitda, income.revenue)

        print(f"{p.label}: Gross Margin = {gross_margin}%, Operating Margin = {operating_margin}%, EBITDA Margin = {ebitda_margin}%")
finally:
    session.close()
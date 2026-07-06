import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import get_periods_for_company, calculate_ebitda
from app.models.income_statement import IncomeStatement
from app.models.cash_flow import CashFlow

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = get_periods_for_company(session, company.id)

    for p in periods:
        income = session.query(IncomeStatement).filter_by(period_id=p.id).first()
        cash = session.query(CashFlow).filter_by(period_id=p.id).first()

        if income is None or cash is None:
            print(f"{p.label}: skipping, missing income statement or cash flow data")
            continue

        ebitda = calculate_ebitda(income.operating_loss, cash.depreciation)
        print(f"{p.label}: Operating Result = {income.operating_loss}, Depreciation = {cash.depreciation}, EBITDA = {ebitda}")
finally:
    session.close()
import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import get_periods_for_company, calculate_capital_employed, calculate_roce_pct
from app.models.income_statement import IncomeStatement
from app.models.balance_sheet import BalanceSheet

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = get_periods_for_company(session, company.id)

    for p in periods:
        income = session.query(IncomeStatement).filter_by(period_id=p.id).first()
        balance = session.query(BalanceSheet).filter_by(period_id=p.id).first()

        if income is None or balance is None:
            print(f"{p.label}: skipping, missing income statement or balance sheet")
            continue

        capital_employed = calculate_capital_employed(balance.fixed_assets, balance.net_current_assets)
        roce = calculate_roce_pct(income.operating_loss, capital_employed)
        print(f"{p.label}: Capital Employed = {capital_employed}, ROCE = {roce}%")
finally:
    session.close()
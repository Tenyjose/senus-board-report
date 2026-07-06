import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import get_periods_for_company, calculate_ebitda, calculate_dscr
from app.models.income_statement import IncomeStatement
from app.models.balance_sheet import BalanceSheet
from app.models.cash_flow import CashFlow

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = get_periods_for_company(session, company.id)

    for p in periods:
        income = session.query(IncomeStatement).filter_by(period_id=p.id).first()
        balance = session.query(BalanceSheet).filter_by(period_id=p.id).first()
        cash = session.query(CashFlow).filter_by(period_id=p.id).first()

        if not income or not balance or not cash:
            print(f"{p.label}: skipping, missing required data")
            continue

        ebitda = calculate_ebitda(income.operating_loss, cash.depreciation)
        dscr = calculate_dscr(ebitda, income.interest_expense, balance.principal_due_within_one_year)
        print(f"{p.label}: EBITDA = {ebitda}, Interest = {income.interest_expense}, Principal Due = {balance.principal_due_within_one_year}, DSCR = {dscr}")
finally:
    session.close()
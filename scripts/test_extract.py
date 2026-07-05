import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company
from app.services.metrics import get_periods_for_company, calculate_revenue_growth_pct
from app.models.income_statement import IncomeStatement

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = get_periods_for_company(session, company.id)

    for p in periods:
        stmt = session.query(IncomeStatement).filter_by(period_id=p.id).first()
        revenue = stmt.revenue if stmt else None
        print(f"{p.label} ({p.start_date} to {p.end_date}): revenue = {revenue}")

    fy2025 = next(p for p in periods if p.label == "FY2025")
    fy2024 = next(p for p in periods if p.label == "FY2024")

    stmt_2025 = session.query(IncomeStatement).filter_by(period_id=fy2025.id).first()
    stmt_2024 = session.query(IncomeStatement).filter_by(period_id=fy2024.id).first()

    growth = calculate_revenue_growth_pct(stmt_2025, stmt_2024)
    print(f"\nFY2025 vs FY2024 revenue growth: {growth}%")
finally:
    session.close()
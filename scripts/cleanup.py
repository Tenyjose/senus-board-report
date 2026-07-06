import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.reporting_period import ReportingPeriod
from app.models.income_statement import IncomeStatement

session = SessionLocal()
try:
    deleted = session.query(IncomeStatement).delete()
    session.commit()
    print(f"Deleted {deleted} existing income_statement rows.")
finally:
    session.close()
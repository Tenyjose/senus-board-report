import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.reporting_period import ReportingPeriod
from app.models.cash_flow import CashFlow

session = SessionLocal()
try:
    deleted = session.query(CashFlow).delete()
    session.commit()
    print(f"Deleted {deleted} existing cash_flow rows.")
finally:
    session.close()
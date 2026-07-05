import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.balance_sheet import BalanceSheet
from app.models.reporting_period import ReportingPeriod

session = SessionLocal()
try:
    bad_period = (
        session.query(ReportingPeriod)
        .filter_by(label="FY2025", start_date="2025-01-01")
        .first()
    )
    if bad_period:
        session.query(BalanceSheet).filter_by(period_id=bad_period.id).delete()
        session.delete(bad_period)
        session.commit()
        print("Cleaned up the incorrect period and its balance sheet row.")
    else:
        print("No matching bad row found - nothing to clean up.")
finally:
    session.close()
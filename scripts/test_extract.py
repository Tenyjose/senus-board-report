import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.reporting_period import ReportingPeriod
from app.models.extraction_log import ExtractionLog

session = SessionLocal()
try:
    for log in session.query(ExtractionLog).all():
        print(f"{log.period.label:25} <- {log.source_doc:35} at {log.extracted_at}")
finally:
    session.close()
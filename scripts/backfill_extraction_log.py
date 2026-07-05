import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.models.company import Company
from app.models.reporting_period import ReportingPeriod
from app.services.db_writer import get_or_create_company, save_extraction_log

# One-time backfill: maps existing periods to the source document they were
# actually extracted from, for extractions done before extraction_log
# existed. extracted_at will reflect backfill time, not original extraction
# time - noted in assumptions log.
SOURCE_DOC_MAP = {
    "FY2024": "adf_farm_solutions_accounts.pdf",
    "FY2025": "adf_farm_solutions_accounts.pdf",
    "HY25": "half_year_results.pdf",
    "HY2025": "half_year_results.pdf",
    "HY2026": "half_year_results.pdf",
    "Snapshot 08-Dec-2025": "senus_balance_sheet.pdf",
}

session = SessionLocal()
try:
    company = get_or_create_company(session)
    periods = session.query(ReportingPeriod).filter_by(company_id=company.id).all()

    for period in periods:
        source_doc = SOURCE_DOC_MAP.get(period.label)
        if source_doc is None:
            print(f"No source doc mapping for label '{period.label}' - skipping")
            continue
        save_extraction_log(session, period, source_doc)
        print(f"Logged: {period.label} <- {source_doc}")

    session.commit()
    print("\nBackfill complete.")
finally:
    session.close()
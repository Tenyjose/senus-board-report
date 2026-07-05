import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.extractor import extract_financials
from app.services.prompts import CASH_FLOW_PROMPT
from app.services.db_writer import get_or_create_company, save_cash_flow
from app.models.cash_flow import CashFlow

with open("docs/source_documents/half_year_results.pdf", "rb") as f:
    pdf_bytes = f.read()

result = extract_financials(pdf_bytes, CASH_FLOW_PROMPT)
print("Extracted:", result)

session = SessionLocal()
try:
    company = get_or_create_company(session)
    for period_data in result["periods"]:
        save_cash_flow(session, company, period_data)
    session.commit()
    print("Saved successfully.")

    print("\n--- What's actually in the database ---")
    for row in session.query(CashFlow).all():
        print(row.period.label, row.operating_cf, row.cash_at_start, row.cash_at_end)
except Exception:
    session.rollback()
    raise
finally:
    session.close()
import sys
sys.path.append("backend")

from app.services.pdf_splitter import extract_pages
from app.services.extractor import extract_financials
from app.services.prompts import BALANCE_SHEET_PROMPT
from app.core.database import SessionLocal
from app.services.db_writer import get_or_create_company, save_balance_sheet
from app.models.balance_sheet import BalanceSheet

pdf_bytes = extract_pages(
    "docs/source_documents/senus_balance_sheet.pdf",
    page_indices=[5]
)

result = extract_financials(pdf_bytes, BALANCE_SHEET_PROMPT)
print("Extracted:", result)

session = SessionLocal()
try:
    company = get_or_create_company(session)
    for period_data in result["periods"]:
        save_balance_sheet(session, company, period_data)
    session.commit()
    print("Saved successfully.")

    print("\n--- What's actually in the database ---")
    for row in session.query(BalanceSheet).all():
        print(row.period.label, row.fixed_assets, row.net_current_assets, row.total_equity)
except Exception:
    session.rollback()
    raise
finally:
    session.close()
import sys
sys.path.append("backend")

from app.core.database import SessionLocal
from app.services.extractor import extract_financials
from app.services.prompts import GROWTH_METRICS_PROMPT
from app.services.db_writer import get_or_create_company, save_customer_metrics
from app.models.customer_metrics import CustomerMetrics

with open("docs/source_documents/half_year_results.pdf", "rb") as f:
    pdf_bytes = f.read()

result = extract_financials(pdf_bytes, GROWTH_METRICS_PROMPT)
print("Extracted:", result)

session = SessionLocal()
try:
    company = get_or_create_company(session)
    save_customer_metrics(session, company, result)
    session.commit()
    print("Saved successfully.")

    print("\n--- What's actually in the database ---")
    for row in session.query(CustomerMetrics).all():
        print(row.period.label, row.total_customers, row.new_deals_closed_value, row.open_pipeline_value, row.notable_commercial_events)
except Exception:
    session.rollback()
    raise
finally:
    session.close()
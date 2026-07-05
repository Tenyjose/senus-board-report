INCOME_STATEMENT_PROMPT = """You are a financial data extraction tool. \
Extract figures from the attached financial statement PDF.

Return ONLY a valid JSON object - no explanation, no markdown, no code fences.

Extract the Income Statement (Profit & Loss) figures for BOTH periods shown. \
Use this exact structure:

{
  "periods": [
    {
      "label": "<short display label, e.g. FY2025 or HY2026>",
      "period_start_date": "<YYYY-MM-DD, based on the period described in the document heading>",
      "period_end_date": "<YYYY-MM-DD>",
      "period_type": "full_year" or "half_year",
      "revenue": <number>,
      "cost_of_sales": <number>,
      "gross_profit": <number>,
      "operating_loss": <number>,
      "net_loss": <number>
    }
  ]
}

Rules:
- Include one object per period shown in the document (usually two).
- Determine period_start_date and period_end_date from the document's own \
heading text (e.g. "for the financial year ended 30 June 2025" means \
period_start_date is 2024-07-01 and period_end_date is 2025-06-30; \
"for the six months ended 31 December 2025" means period_start_date is \
2025-07-01 and period_end_date is 2025-12-31).
- Use plain numbers only: no currency symbols, no commas, no text.
- cost_of_sales must always be returned as a negative number, representing \
a reduction from revenue, regardless of whether the source document shows \
it as positive or in brackets.
- All other losses and negative figures must be negative numbers (e.g. -590256).
- If a figure is genuinely not present in the document, use null. \
Never guess or invent a number.
- Match figures to the correct period exactly as labelled in the document."""


BALANCE_SHEET_PROMPT = """You are a financial data extraction tool. \
Extract figures from the attached financial statement PDF.

Return ONLY a valid JSON object - no explanation, no markdown, no code fences.

Context: this company's fiscal year runs from 1 July to 30 June.

Extract the Balance Sheet figures for BOTH periods shown. Use this exact \
structure:

{
  "periods": [
    {
      "label": "<short display label, see rules below>",
      "period_start_date": "<YYYY-MM-DD>",
      "period_end_date": "<YYYY-MM-DD>",
      "period_type": "full_year", "half_year", or "snapshot",
      "fixed_assets": <number>,
      "current_assets": <number>,
      "creditors_due_within_one_year": <number>,
      "net_current_assets": <number>,
      "creditors_due_after_one_year": <number>,
      "net_assets": <number>,
      "share_capital": <number>,
      "share_premium": <number>,
      "retained_earnings": <number>,
      "total_equity": <number>
    }
  ]
}

Rules:
- Include one object per period shown in the document (this may be one or two).
- A balance sheet is described as "as at" a single date. Determine which \
kind of period it represents:
  - If the "as at" date is exactly the fiscal year end (30 June), this is \
period_type "full_year": period_start_date is 1 July of the prior calendar \
year, period_end_date is the "as at" date, label is "FY<year>".
  - If the "as at" date is exactly 31 December (the mid-point of the fiscal \
year), this is period_type "half_year": period_start_date is 1 July of that \
same calendar year, period_end_date is the "as at" date, label is "HY<year+1>".
  - If the "as at" date does NOT match either of those (e.g. a one-off \
snapshot for a listing or other event), this is period_type "snapshot": \
set BOTH period_start_date and period_end_date to the "as at" date itself, \
and label as "Snapshot <DD-Mon-YYYY>".
- Use plain numbers only: no currency symbols, no commas, no text.
- Liabilities and deficits must be negative numbers.
- If a figure is genuinely not present in the document, use null. \
Never guess or invent a number.
- Match figures to the correct period exactly as labelled in the document."""



CASH_FLOW_PROMPT = """You are a financial data extraction tool. \
Extract figures from the attached financial statement PDF.

Return ONLY a valid JSON object - no explanation, no markdown, no code fences.

Extract the Cash Flow Statement figures for BOTH periods shown. Use this \
exact structure:

{
  "periods": [
    {
      "label": "<short display label, e.g. FY2025 or HY2026>",
      "period_start_date": "<YYYY-MM-DD, based on the period described in the document heading>",
      "period_end_date": "<YYYY-MM-DD>",
      "period_type": "full_year" or "half_year",
      "net_cash_from_operating": <number>,
      "net_cash_from_investing": <number>,
      "net_cash_from_financing": <number>,
      "cash_at_start": <number>,
      "cash_at_end": <number>
    }
  ]
}

Rules:
- Include one object per period shown in the document (usually two).
- Determine period_start_date and period_end_date from the document's own \
heading text, the same way an income statement or cash flow date range \
is described (e.g. "for the six months ended 31 December 2025").
- Use plain numbers only: no currency symbols, no commas, no text.
- Cash outflows must be negative numbers.
- If a figure is genuinely not present in the document, use null. \
Never guess or invent a number.
- Match figures to the correct period exactly as labelled in the document."""


GROWTH_METRICS_PROMPT = """You are a financial data extraction tool. \
Extract growth and commercial metrics from the attached document. This \
data typically appears in narrative text (highlights, commentary), not in \
formal tables - read carefully.

Return ONLY a valid JSON object - no explanation, no markdown, no code fences.

Use this exact structure:

{
  "label": "<short display label for the period this commentary describes, e.g. HY2026>",
  "period_start_date": "<YYYY-MM-DD>",
  "period_end_date": "<YYYY-MM-DD>",
  "period_type": "full_year" or "half_year",
  "revenue_growth_pct": <number or null>,
  "gross_margin_pct": <number or null>,
  "total_customer_accounts": <number or null, ONLY if the document states an \
overall/total customer count - not a subset involved in one deal batch>,
  "deal_batches_mentioned": [
    {
      "description": "<short label, e.g. 'deals closed in final two months'>",
      "deal_count": <number or null>,
      "customers_involved": <number or null>,
      "combined_value": <number or null>
    }
  ],
  "open_pipeline_value": <number or null>,
  "notable_commercial_events": [<short string>, ...]
}

Rules:
- The period fields describe the CURRENT/most recent period covered by the \
document's narrative, not a prior comparison period.
- Percentages as plain numbers (e.g. 4.1, not "4.1%" or 0.041).
- Monetary values as plain numbers in the document's base currency unit \
(e.g. if the document says "€700k", return 700000).
- Include a separate entry in deal_batches_mentioned for EACH distinct group \
of deals described in the text, even if they overlap in time period.
- notable_commercial_events should be a short list (max 5) of concrete \
named events only, not general commentary or opinions.
- If a figure is genuinely not present in the document, use null or an \
empty list. Never guess or invent a number."""
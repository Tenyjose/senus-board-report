# Senus Board Report

I built this Project for Assiduous's technical assignment - an AI-native board report for
Senus PLC, a real Irish Natural Capital management company listed on Euronext Access
Dublin. This is the full thing, live and deployed.

Some relevant links are added below:

**Live app:** https://senus-board-report-lyart.vercel.app/
**Demo video**: https://youtu.be/U62XmAHfJCQ


## What this actually is

Real board reports get built by hand. Someone in finance pulls numbers out of PDFs
and spreadsheets, works out the ratios, writes some commentary, and it takes days —
and two people doing it might not do it quite the same way.

I wanted to see how much of that could actually run itself. So this reads the real
audited financial statements for Senus (some of them scanned images with no text
layer at all), pulls structured numbers out using Claude, stores them properly in a
database, calculates the metrics a board actually cares about, and has Claude write
grounded commentary on top of the numbers it already trusts. It's served through a
dashboard styled to look like a real financial statement rather than a generic
analytics template.

It covers everything the brief asked for: Growth & Revenue, Profitability, Cash &
Liquidity, Solvency & Leverage, and Returns.

## How it's put together

```
Source PDFs (4 documents, some scanned, some text)
        |
        v
Extraction  ->  Claude reads each statement type off the PDF and returns strict JSON.
                One prompt per statement (income statement, balance sheet, cash flow,
                growth narrative), so each one's easy to debug on its own.
        |
        v
Database  ->  Neon Postgres, 7 tables. Everything gets saved with a get-or-create
              check first, so re-running the pipeline never creates duplicates.
        |
        v
Metrics engine  ->  Plain Python, no AI here at all. Reads the stored numbers back
                     out and calculates revenue growth, margins, EBITDA, working
                     capital, cash runway, DSCR, ROCE — all of it deterministic.
        |
        v
AI insights  ->  A second, separate Claude call. It only ever sees the already-
                  calculated metrics, never the raw PDFs, and it's explicitly told
                  not to reference anything that isn't in the data I hand it.
        |
        v
API  ->  FastAPI. Three endpoints: /periods/, /periods/{id}/metrics,
         /periods/{id}/insights
        |
        v
Frontend  ->  React + Recharts
```

I kept these as separate steps on purpose. The frontend never talks to Claude
directly, the metrics engine never touches a PDF — so if a number ever looks wrong,
I know exactly which layer to go check.

## Stack

Python, FastAPI, SQLAlchemy, Alembic for migrations, Postgres on Neon, Claude
(`claude-opus-4-8`) for both extraction and commentary, `pypdf` for splitting out
pages from oversized scanned documents. React (Vite) and Recharts on the frontend.
Backend's deployed on Render, frontend on Vercel.

## How I used Claude

Three genuinely different ways, not one AI call bolted onto the side:

1. As a pairing partner for the whole build — walking through every new concept
   before writing code, and diagnosing real errors from the actual traceback instead
   of guessing at fixes.
2. As the extraction engine — sending PDF pages to Claude's vision and getting back
   structured JSON I could trust and check.
3. As the commentary layer — a second call that only sees numbers I've already
   verified, and is locked down to never invent a figure or event that isn't
   actually in the data.

This wasn't a clean, linear build. I hit real bugs along the way and fixed them as
I found them — a couple are worth calling out below, since they're a better sign of
how the extraction actually holds up than pretending everything worked first try.

## Calls I had to make along the way

- **ADF Farm Solutions Limited and Senus PLC are the same company.** I first
  suspected this because the FY2025 revenue figure matched exactly (€836,991) across
  two separate documents, and later found it stated directly — one document's header
  literally says "Senus Limited (formerly ADF Farm Solutions Limited)."
- **Senus's financial year runs 1 July to 30 June.** Half-year periods run 1 July to
  31 December.
- **EBITDA isn't disclosed anywhere directly**, so I calculate it as Operating Result
  plus Depreciation (the real figure from the cash flow statement) plus Amortisation,
  which defaults to 0 since it's never broken out separately in any of the source
  documents.
- **`cost_of_sales` is always stored as a negative number**, no matter how the source
  document displays it. One document showed it in brackets, another as a plain
  positive number — I made the sign rule explicit in the prompt so it's consistent
  either way.
- **Periods get matched by date range, not by whatever label Claude extracts.** The
  same real period came back labelled `"HY25"` in one call and `"HY2025"` in another
  — matching on actual dates instead avoided quietly creating a duplicate.
- **The 8 December 2025 balance sheet gets its own period type, "snapshot."** It
  doesn't line up with either a full year or a half year — it's a one-off document
  prepared ahead of the Euronext listing, so forcing it into either shape would have
  been wrong.
- **A dash in the source document is treated as zero**, not as missing data, since
  that's the standard accounting convention and the downstream maths needs an actual
  number to work with.
- **DSCR only shows up where real debt actually exists.** There was no debt at all in
  FY2024, and the half-year documents don't disclose a full repayment schedule, so I
  left it null there rather than fake a number.
- **I left `enterprise_pct` null.** The only related figure in the source text
  describes customers tied to one specific batch of deals, not the company's total
  customer base — turning that into a percentage would have implied more precision
  than the data actually supports.

## How I checked the numbers were actually right

I didn't just trust that the code ran without errors — I checked the real figures
against the source PDFs by hand at every stage. A couple of things came out of that:

Cash balances chain correctly across periods that were extracted completely
independently — FY2024's closing cash exactly equals FY2025's opening cash, which
equals HY2026's opening cash. Those three numbers came from separate API calls on
separate documents, so that agreement is stronger evidence than checking any single
figure in isolation.

Capital Employed also lines up with a figure the source documents state directly
("Total Assets less Current Liabilities"), which is a good independent check on the
formula rather than just trusting the derived calculation.

Two real bugs, found and fixed with before/after proof:
- `cost_of_sales` came back with a different sign in different documents at first,
  because Claude was following each document's own formatting instead of a fixed
  rule — fixed by making the sign explicit in the prompt regardless of source
  formatting.
- Period dates were originally guessed from a hardcoded label lookup (`"FY2025"` →
  a fixed date range), which broke the moment a document used a slightly different
  label. Fixed by having Claude read the real date range straight out of each
  document's own heading instead.

## Project layout

```
backend/app/
  api/            FastAPI routes — periods, metrics, insights
  core/           config and database connection
  models/         the 7 SQLAlchemy tables
  services/
    extractor.py    sends a PDF to Claude, parses the JSON back
    pdf_splitter.py  pulls specific pages out of an oversized PDF
    prompts.py       the extraction prompts, one per statement type
    db_writer.py     get-or-create save functions
    metrics.py       the actual calculations
    insights.py      the AI commentary call
  alembic/        migration history
frontend/src/
  App.jsx         the dashboard — period picker, ledger, charts, AI summary
  index.css       styling
docs/source_documents/   the original PDFs
scripts/          scratch scripts I used to verify things while building
```

## Running it locally

Backend:
```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# .env needs DATABASE_URL and ANTHROPIC_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```
cd frontend
npm install
# .env needs VITE_API_BASE_URL=http://127.0.0.1:8000
npm run dev
```

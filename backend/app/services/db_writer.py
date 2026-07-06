from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.reporting_period import ReportingPeriod
from app.models.income_statement import IncomeStatement
from app.models.balance_sheet import BalanceSheet
from app.models.cash_flow import CashFlow
from app.models.customer_metrics import CustomerMetrics
from app.models.extraction_log import ExtractionLog

SENUS_COMPANY_NAME = "Senus PLC"
SENUS_TICKER = "SENUS"


def get_or_create_company(session: Session) -> Company:
    company = session.query(Company).filter_by(name=SENUS_COMPANY_NAME).first()
    if company is None:
        company = Company(name=SENUS_COMPANY_NAME, ticker=SENUS_TICKER)
        session.add(company)
        session.flush()
    return company


def get_or_create_reporting_period(session: Session, company: Company, period_data: dict) -> ReportingPeriod:
    start_date = period_data["period_start_date"]
    end_date = period_data["period_end_date"]

    period = (
        session.query(ReportingPeriod)
        .filter_by(company_id=company.id, start_date=start_date, end_date=end_date)
        .first()
    )
    if period is None:
        period = ReportingPeriod(
            company_id=company.id,
            label=period_data["label"],
            start_date=start_date,
            end_date=end_date,
            period_type=period_data["period_type"],
        )
        session.add(period)
        session.flush()
    return period


def save_extraction_log(session: Session, period: ReportingPeriod, source_doc: str) -> ExtractionLog:
    existing = (
        session.query(ExtractionLog)
        .filter_by(period_id=period.id, source_doc=source_doc)
        .first()
    )
    if existing:
        return existing

    log_entry = ExtractionLog(
        period_id=period.id,
        source_doc=source_doc,
        extracted_at=datetime.now(timezone.utc),
    )
    session.add(log_entry)
    return log_entry


def save_income_statement(session: Session, company: Company, period_data: dict, source_doc: str) -> IncomeStatement:
    period = get_or_create_reporting_period(session, company, period_data)
    save_extraction_log(session, period, source_doc)

    existing = session.query(IncomeStatement).filter_by(period_id=period.id).first()
    if existing:
        return existing

    income_statement = IncomeStatement(
        period_id=period.id,
        revenue=period_data["revenue"],
        cost_of_sales=period_data["cost_of_sales"],
        gross_profit=period_data["gross_profit"],
        operating_loss=period_data["operating_loss"],
        interest_expense=period_data.get("interest_expense"),
        net_loss=period_data["net_loss"],
    )
    session.add(income_statement)
    return income_statement


def save_balance_sheet(session: Session, company: Company, period_data: dict, source_doc: str) -> BalanceSheet:
    period = get_or_create_reporting_period(session, company, period_data)
    save_extraction_log(session, period, source_doc)

    existing = session.query(BalanceSheet).filter_by(period_id=period.id).first()
    if existing:
        return existing

    balance_sheet = BalanceSheet(
        period_id=period.id,
        fixed_assets=period_data["fixed_assets"],
        current_assets=period_data["current_assets"],
        creditors_due_within_one_year=period_data["creditors_due_within_one_year"],
        net_current_assets=period_data["net_current_assets"],
        creditors_due_after_one_year=period_data["creditors_due_after_one_year"],
        net_assets=period_data["net_assets"],
        share_capital=period_data["share_capital"],
        share_premium=period_data["share_premium"],
        retained_earnings=period_data["retained_earnings"],
        total_equity=period_data["total_equity"],
    )
    session.add(balance_sheet)
    return balance_sheet


def save_cash_flow(session: Session, company: Company, period_data: dict, source_doc: str) -> CashFlow:
    period = get_or_create_reporting_period(session, company, period_data)
    save_extraction_log(session, period, source_doc)

    existing = session.query(CashFlow).filter_by(period_id=period.id).first()
    if existing:
        return existing

    cash_flow = CashFlow(
        period_id=period.id,
        operating_cf=period_data["net_cash_from_operating"],
        investing_cf=period_data["net_cash_from_investing"],
        financing_cf=period_data["net_cash_from_financing"],
        cash_at_start=period_data["cash_at_start"],
        cash_at_end=period_data["cash_at_end"],
        depreciation=period_data.get("depreciation"),
    )
    session.add(cash_flow)
    return cash_flow


def save_customer_metrics(session: Session, company: Company, period_data: dict, source_doc: str) -> CustomerMetrics:
    period = get_or_create_reporting_period(session, company, period_data)
    save_extraction_log(session, period, source_doc)

    existing = session.query(CustomerMetrics).filter_by(period_id=period.id).first()
    if existing:
        return existing

    total_new_deals_value = sum(
        batch["combined_value"] or 0
        for batch in period_data.get("deal_batches_mentioned", [])
    )

    customer_metrics = CustomerMetrics(
        period_id=period.id,
        total_customers=period_data.get("total_customer_accounts"),
        enterprise_pct=None,
        new_deals_closed_value=total_new_deals_value,
        open_pipeline_value=period_data.get("open_pipeline_value"),
        notable_commercial_events=period_data.get("notable_commercial_events", []),
    )
    session.add(customer_metrics)
    return customer_metrics


def update_balance_sheet_loan_schedule(session: Session, as_at_date, principal_due_within_one_year) -> BalanceSheet | None:
    period = (
        session.query(ReportingPeriod)
        .filter_by(end_date=as_at_date)
        .first()
    )
    if period is None:
        print(f"No reporting period found ending {as_at_date} - cannot attach loan schedule")
        return None

    balance_sheet = session.query(BalanceSheet).filter_by(period_id=period.id).first()
    if balance_sheet is None:
        print(f"No balance sheet found for period ending {as_at_date}")
        return None

    balance_sheet.principal_due_within_one_year = principal_due_within_one_year
    return balance_sheet
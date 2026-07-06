from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class BalanceSheet(Base):
    __tablename__ = "balance_sheet"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    fixed_assets = Column(Numeric(14, 2))
    current_assets = Column(Numeric(14, 2))
    creditors_due_within_one_year = Column(Numeric(14, 2))
    net_current_assets = Column(Numeric(14, 2))
    creditors_due_after_one_year = Column(Numeric(14, 2))
    net_assets = Column(Numeric(14, 2))
    share_capital = Column(Numeric(14, 2))
    share_premium = Column(Numeric(14, 2))
    retained_earnings = Column(Numeric(14, 2))
    total_equity = Column(Numeric(14, 2))
    principal_due_within_one_year = Column(Numeric(14, 2))

    period = relationship("ReportingPeriod")
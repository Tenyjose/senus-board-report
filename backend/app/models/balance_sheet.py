from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class BalanceSheet(Base):
    __tablename__ = "balance_sheet"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    cash = Column(Numeric(14, 2))
    debtors = Column(Numeric(14, 2))
    creditors = Column(Numeric(14, 2))
    net_assets = Column(Numeric(14, 2))

    period = relationship("ReportingPeriod")
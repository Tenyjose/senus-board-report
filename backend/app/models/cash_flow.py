from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CashFlow(Base):
    __tablename__ = "cash_flow"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    operating_cf = Column(Numeric(14, 2))
    investing_cf = Column(Numeric(14, 2))
    financing_cf = Column(Numeric(14, 2))

    period = relationship("ReportingPeriod")
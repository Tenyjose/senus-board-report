from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class IncomeStatement(Base):
    __tablename__ = "income_statement"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    revenue = Column(Numeric(14, 2))
    cost_of_sales = Column(Numeric(14, 2))
    gross_profit = Column(Numeric(14, 2))
    operating_loss = Column(Numeric(14, 2))
    net_loss = Column(Numeric(14, 2))
    interest_expense = Column(Numeric(14, 2))

    period = relationship("ReportingPeriod")
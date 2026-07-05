from sqlalchemy import Column, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class CustomerMetrics(Base):
    __tablename__ = "customer_metrics"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    total_customers = Column(Integer)
    enterprise_pct = Column(Numeric(5, 2))

    period = relationship("ReportingPeriod")
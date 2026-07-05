
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class ExtractionLog(Base):
    __tablename__ = "extraction_log"

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey("reporting_periods.id"), nullable=False)
    source_doc = Column(String, nullable=False)
    extracted_at = Column(DateTime, nullable=False)

    period = relationship("ReportingPeriod")
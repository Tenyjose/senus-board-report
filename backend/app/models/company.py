
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    ticker = Column(String, nullable=True)
    reporting_periods = relationship("ReportingPeriod", back_populates="company")

    
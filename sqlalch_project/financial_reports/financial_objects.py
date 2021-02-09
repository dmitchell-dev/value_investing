from sqlalchemy import Column, ForeignKey, Integer, Float, DateTime
from ..common.mysql_base import Base


class FinancialObjects(Base):
    __tablename__ = "reporting_data"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    parameter_id = Column(Integer, ForeignKey("parameters.id"), nullable=False)
    time_stamp = Column(DateTime)
    value = Column(Float)

from sqlalchemy import Column, ForeignKey, Integer, String, Float, Text
from ..common.mysql_base import Base


class Markets(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True)
    share_listing = Column(String(255))


class CompanyType(Base):
    __tablename__ = "company_type"

    id = Column(Integer, primary_key=True)
    company_type = Column(String(255))


class IndustryRisk(Base):
    __tablename__ = "industry_risk"

    id = Column(Integer, primary_key=True)
    industry_type = Column(String(255))


class ReportType(Base):
    __tablename__ = "report_type"

    id = Column(Integer, primary_key=True)
    report_name = Column(String(255))


class Industries(Base):
    __tablename__ = "industries"

    id = Column(Integer, primary_key=True)
    industry_risk_id = Column(Integer, ForeignKey("industry_risk.id"), nullable=False)
    industry_name = Column(String(255))


class ReportSection(Base):
    __tablename__ = "report_section"

    id = Column(Integer, primary_key=True)
    report_type_id = Column(Integer, ForeignKey("report_type.id"), nullable=False)
    report_section = Column(String(255))
    report_section_last = Column(String(255))


class Params(Base):
    __tablename__ = "params"

    id = Column(Integer, primary_key=True)
    report_section_id = Column(Integer, ForeignKey("report_section.id"), nullable=False)
    param_name = Column(String(255))
    limit_logic = Column(String(255))
    limit_value = Column(String(255))
    param_description = Column(String(255))


class CalcVariables(Base):
    __tablename__ = "calc_variables"

    id = Column(Integer, primary_key=True)
    parameter_id = Column(Integer, ForeignKey("params.id"), nullable=False)
    value = Column(Float)


class Companies(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    comp_type_id = Column(Integer, ForeignKey("company_type.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.id"), nullable=False)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    tidm = Column(String(10))
    company_name = Column(String(255))
    company_summary = Column(Text)

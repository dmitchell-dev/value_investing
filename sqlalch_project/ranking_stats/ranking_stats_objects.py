from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        DateTime,
                        String
                        )
from ..common.mysql_base import Base


class RankingStatsObjects(Base):
    __tablename__ = 'ranking_data'

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
        )
    parameter_id = Column(
        Integer,
        ForeignKey("parameters.id"),
        nullable=False
        )
    time_stamp = Column(DateTime)
    value = Column(String(255))

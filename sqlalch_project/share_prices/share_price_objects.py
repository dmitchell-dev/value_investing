from sqlalchemy import (Column,
                        ForeignKey,
                        Integer,
                        Float,
                        DateTime,
                        SmallInteger
                        )
from ..common.mysql_base import Base


class SharePriceObjects(Base):
    __tablename__ = 'share_price'

    id = Column(Integer, primary_key=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False
        )
    time_stamp = Column(DateTime)
    value = Column(Float)
    volume = Column(Integer)
    adjustment = Column(SmallInteger)

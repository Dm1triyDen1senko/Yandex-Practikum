from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String

from models.base import Base


class Metric(Base):
    __tablename__ = 'metric'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer)
    action = Column(String(1000))
    data = Column(String(1000))
    timestamp = Column(DateTime, default=datetime.utcnow)

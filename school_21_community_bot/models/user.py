from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime,
                        ForeignKey, BigInteger, String)

from models.base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    full_name = Column(String(256))
    role = Column(String(256),
                  ForeignKey('role.name', name='fk_user_name_role'))
    level = Column(String(50),
                   ForeignKey('level.name', name='fk_user_name_level'))
    team = Column(String(256), nullable=False)
    project = Column(String(1024))
    telegram_nick = Column(String(32), nullable=False)
    sberchat_nick = Column(String(256), nullable=False)
    school21_nick = Column(String(16), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    invite_sent = Column(Boolean, default=False)
    is_member = Column(Boolean, default=False)

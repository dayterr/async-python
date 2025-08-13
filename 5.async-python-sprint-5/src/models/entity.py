from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from src.db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    password = Column(String(100))


class File(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    path = Column(String(250), unique=True)
    size = Column(Integer)
    is_downloadable = Column(Boolean)
    user = Column(Integer, ForeignKey('users.id'))


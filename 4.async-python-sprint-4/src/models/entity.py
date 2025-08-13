from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    password = Column(String(100))


class ShortenedUrl(Base):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    full_url = Column(String(200), nullable=False)
    short_url = Column(String(100), nullable=False)
    clicks = Column(Integer, default=0)
    type = Column(String(100), nullable=True)
    is_deleted = Column(Boolean)
    user = Column(Integer, ForeignKey('users.id'), nullable=True)

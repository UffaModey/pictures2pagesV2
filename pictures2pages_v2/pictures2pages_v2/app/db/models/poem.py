# app/db/models/user.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Poem(Base):
    __tablename__ = "poems"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="poems")

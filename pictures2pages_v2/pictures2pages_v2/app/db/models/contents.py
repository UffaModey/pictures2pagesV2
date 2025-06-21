# app/db/models/user.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class GeneratedContent(Base):
    __tablename__ = "generated_content"
    id = Column(Integer, primary_key=True, index=True)
    is_story = Column(Boolean, default=True)
    content = Column(Text, nullable=False)
    title = Column(Text, nullable=False)
    theme = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    image_url_1 = Column(String, nullable=False)
    image_url_2 = Column(String, nullable=False)
    image_url_3 = Column(String, nullable=False)
    caption_1 = Column(String, nullable=False)
    caption_2 = Column(String, nullable=False)
    caption_3 = Column(String, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="generated_contents")

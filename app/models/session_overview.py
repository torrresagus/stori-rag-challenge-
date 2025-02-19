# app/models/session_overview.py
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.db.db import Base

metadata = Base.metadata


class SessionOverview(Base):
    __tablename__ = "session_overview"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False)
    auto_faithfulness = Column(Float, nullable=True)
    auto_relevance = Column(Float, nullable=True)
    auto_correctness = Column(Float, nullable=True)
    auto_comments = Column(String, nullable=True)
    human_faithfulness = Column(Float, nullable=True)
    human_relevance = Column(Float, nullable=True)
    human_correctness = Column(Float, nullable=True)
    human_comments = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

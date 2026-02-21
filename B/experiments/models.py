# experiments/models.py
# SQLAlchemy model for the Experiment table.
# Why: Keeps the experiment schema co-located with experiment routes and templates.
# Relevant files: experiments/schemas.py, experiments/routes.py, runs/models.py

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from shared.base import Base


class ExperimentStatus(str, enum.Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Experiment id={self.id} name={self.name!r} status={self.status.value}>"

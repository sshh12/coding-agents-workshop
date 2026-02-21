# runs/models.py
# SQLAlchemy model for the Run table (individual experiment runs with metrics).
# Why: Keeps run schema co-located with run routes; separate from experiment models.
# Relevant files: runs/schemas.py, runs/routes.py, experiments/models.py

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from shared.base import Base


class RunStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    name = Column(String, default="")
    hyperparameters = Column(Text, default="{}")
    accuracy = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    notes = Column(Text, default="")
    status = Column(Enum(RunStatus), default=RunStatus.COMPLETED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="runs")

    def __repr__(self):
        return f"<Run id={self.id} experiment_id={self.experiment_id} status={self.status.value}>"

# exports/models.py
# SQLAlchemy model for the ExportJob table (tracks export requests and their status).
# Why: Keeps export schema co-located with export routes; tracks async-style jobs.
# Relevant files: exports/schemas.py, exports/routes.py, experiments/models.py

import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, Text

from shared.base import Base


class ExportFormat(str, enum.Enum):
    JSON = "json"
    CSV = "csv"


class ExportJob(Base):
    __tablename__ = "export_jobs"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, nullable=False)
    format = Column(Enum(ExportFormat), default=ExportFormat.JSON, nullable=False)
    result = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExportJob id={self.id} experiment_id={self.experiment_id} format={self.format.value}>"

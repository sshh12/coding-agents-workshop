# tags/models.py
# SQLAlchemy model for the Tag table (experiment labels for filtering and grouping).
# Why: Keeps tag schema co-located with tag routes; many-to-many with experiments.
# Relevant files: tags/schemas.py, tags/routes.py, experiments/models.py

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from shared.base import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="tags")

    __table_args__ = (
        UniqueConstraint("experiment_id", "name", name="uq_experiment_tag"),
    )

    def __repr__(self):
        return f"<Tag id={self.id} name={self.name!r} experiment_id={self.experiment_id}>"

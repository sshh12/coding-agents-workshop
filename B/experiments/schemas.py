# experiments/schemas.py
# Pydantic schemas for experiment API request/response validation.
# Why: Separates validation from DB models; gives agents clear input/output contracts.
# Relevant files: experiments/models.py, experiments/routes.py

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from experiments.models import ExperimentStatus


class ExperimentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Experiment name")
    description: str = Field(default="", max_length=2000, description="Experiment description")
    status: ExperimentStatus = Field(default=ExperimentStatus.DRAFT, description="Initial status")


class ExperimentResponse(BaseModel):
    id: int
    name: str
    description: str
    status: ExperimentStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    total_runs: int = 0
    avg_accuracy: Optional[float] = None

    model_config = {"from_attributes": True}


class ExperimentDetailResponse(ExperimentResponse):
    runs: list = Field(default_factory=list)

# runs/schemas.py
# Pydantic schemas for run API request/response validation.
# Why: Typed contracts prevent stringly-typed metrics and invalid hyperparameters.
# Relevant files: runs/models.py, runs/routes.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from runs.models import RunStatus


class RunCreate(BaseModel):
    name: str = Field(default="", max_length=200, description="Run name or label")
    hyperparameters: dict = Field(default_factory=dict, description="Hyperparameter dict (e.g. {'lr': 0.001})")
    accuracy: Optional[float] = Field(default=None, ge=0, le=1, description="Accuracy metric (0-1)")
    loss: Optional[float] = Field(default=None, ge=0, description="Loss metric")
    latency_ms: Optional[float] = Field(default=None, ge=0, description="Latency in milliseconds")
    notes: str = Field(default="", max_length=5000, description="Free-form notes")
    status: RunStatus = Field(default=RunStatus.COMPLETED, description="Run status")


class RunResponse(BaseModel):
    id: int
    experiment_id: int
    name: str
    hyperparameters: dict
    accuracy: Optional[float] = None
    loss: Optional[float] = None
    latency_ms: Optional[float] = None
    notes: str = ""
    status: RunStatus
    created_at: datetime

    model_config = {"from_attributes": True}

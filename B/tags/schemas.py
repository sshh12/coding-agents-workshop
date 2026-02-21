# tags/schemas.py
# Pydantic schemas for tag API request/response validation.
# Why: Typed contracts for tag endpoints; validates name length and format.
# Relevant files: tags/models.py, tags/routes.py

from datetime import datetime

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Tag name (e.g. 'nlp', 'production', 'baseline')")


class TagResponse(BaseModel):
    id: int
    experiment_id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}

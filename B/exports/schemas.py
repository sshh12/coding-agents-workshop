# exports/schemas.py
# Pydantic schemas for export API request/response validation.
# Why: Typed contracts for export endpoints; validates format enum.
# Relevant files: exports/models.py, exports/routes.py

from datetime import datetime

from pydantic import BaseModel, Field

from exports.models import ExportFormat


class ExportRequest(BaseModel):
    format: ExportFormat = Field(default=ExportFormat.JSON, description="Export format: json or csv")


class ExportResponse(BaseModel):
    id: int
    experiment_id: int
    format: ExportFormat
    result: str
    created_at: datetime

    model_config = {"from_attributes": True}

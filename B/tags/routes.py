# tags/routes.py
# API routes for experiment tagging.
# Why: Co-locates all tag endpoints; agents find them by folder name.
# Relevant files: tags/models.py, tags/schemas.py, experiments/models.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from experiments.models import Experiment
from shared.db import get_db
from tags.models import Tag
from tags.schemas import TagCreate, TagResponse  # noqa: F401 – TagCreate used by TODO endpoint below

router = APIRouter()


@router.get("/api/experiments/{experiment_id}/tags", response_model=list[TagResponse])
def list_tags(experiment_id: int, db: Session = Depends(get_db)):
    """List all tags for an experiment.

    Returns 404 if the experiment does not exist.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found. Check the ID and try again.",
        )
    tags = db.query(Tag).filter(Tag.experiment_id == experiment_id).all()
    return [
        TagResponse(
            id=t.id,
            experiment_id=t.experiment_id,
            name=t.name,
            created_at=t.created_at,
        )
        for t in tags
    ]


# TODO: Add POST endpoint for creating tags.
# Follow the pattern in runs/routes.py (see create_run function).
# Accept TagCreate schema as JSON body.
# Return TagResponse with status_code=201.
# Handle 404 (experiment not found) and 409 (duplicate tag name).
# See tests/test_tags.py for expected behavior and response format.

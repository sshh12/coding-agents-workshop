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
from tags.schemas import TagCreate, TagResponse

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


# TODO: Add POST /api/experiments/{experiment_id}/tags endpoint
# Should accept a TagCreate body, validate the experiment exists,
# check for duplicate tag names, and return 201 with TagResponse.
# Follow the pattern in runs/routes.py create_run() for reference.

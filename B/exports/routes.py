# exports/routes.py
# API routes for exporting experiment data.
# Why: Co-locates all export endpoints; agents find them by folder name.
# Relevant files: exports/models.py, exports/schemas.py, experiments/models.py

from __future__ import annotations

import csv
import io
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from experiments.models import Experiment
from exports.models import ExportFormat, ExportJob
from exports.schemas import ExportRequest, ExportResponse
from shared.db import get_db

router = APIRouter()


@router.post("/api/experiments/{experiment_id}/export", response_model=ExportResponse, status_code=201)
def export_experiment(experiment_id: int, payload: ExportRequest, db: Session = Depends(get_db)):
    """Export experiment data in the requested format.

    Returns 404 if the experiment does not exist.
    Returns 201 with the export result on success.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found. Check the ID and try again.",
        )

    runs_data = []
    for run in experiment.runs:
        hp = json.loads(run.hyperparameters) if run.hyperparameters else {}
        runs_data.append({
            "id": run.id,
            "name": run.name,
            "hyperparameters": hp,
            "accuracy": run.accuracy,
            "loss": run.loss,
            "latency_ms": run.latency_ms,
            "status": run.status.value,
        })

    if payload.format == ExportFormat.JSON:
        result = json.dumps({
            "experiment": {
                "id": experiment.id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status.value,
            },
            "runs": runs_data,
        }, indent=2)
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "name", "accuracy", "loss", "latency_ms", "status"])
        writer.writeheader()
        for run in runs_data:
            writer.writerow({k: run[k] for k in ["id", "name", "accuracy", "loss", "latency_ms", "status"]})
        result = output.getvalue()

    job = ExportJob(
        experiment_id=experiment_id,
        format=payload.format,
        result=result,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return ExportResponse(
        id=job.id,
        experiment_id=job.experiment_id,
        format=job.format,
        result=job.result,
        created_at=job.created_at,
    )

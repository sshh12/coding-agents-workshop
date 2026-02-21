# runs/routes.py
# API and HTML routes for logging runs and comparing metrics.
# Why: Co-locates all run endpoints; agents find them by folder name.
# Relevant files: runs/models.py, runs/schemas.py, runs/templates/, experiments/models.py

from __future__ import annotations

import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from experiments.models import Experiment, ExperimentStatus
from runs.models import Run, RunStatus
from runs.schemas import RunCreate, RunResponse
from shared.db import get_db

router = APIRouter()

_template_dir = os.path.join(os.path.dirname(__file__), "templates")
_shared_template_dir = os.path.join(os.path.dirname(__file__), "..", "shared", "templates")
templates = Jinja2Templates(directory=[_template_dir, _shared_template_dir])


def _format_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


# --- API Routes ---


@router.post("/api/experiments/{experiment_id}/runs", response_model=RunResponse, status_code=201)
def create_run(experiment_id: int, payload: RunCreate, db: Session = Depends(get_db)):
    """Log a new run for an experiment.

    Returns 404 if the experiment does not exist.
    Returns 201 with the created run on success.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found. Create the experiment first with POST /api/experiments.",
        )
    run = Run(
        experiment_id=experiment_id,
        name=payload.name,
        hyperparameters=json.dumps(payload.hyperparameters),
        accuracy=payload.accuracy,
        loss=payload.loss,
        latency_ms=payload.latency_ms,
        notes=payload.notes,
        status=payload.status,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return RunResponse(
        id=run.id,
        experiment_id=run.experiment_id,
        name=run.name,
        hyperparameters=json.loads(run.hyperparameters),
        accuracy=run.accuracy,
        loss=run.loss,
        latency_ms=run.latency_ms,
        notes=run.notes,
        status=run.status,
        created_at=run.created_at,
    )


@router.get("/api/experiments/{experiment_id}/runs/{run_id}", response_model=RunResponse)
def get_run(experiment_id: int, run_id: int, db: Session = Depends(get_db)):
    """Get details for a specific run.

    Returns 404 if the run does not exist or does not belong to the experiment.
    """
    run = db.query(Run).filter(Run.id == run_id, Run.experiment_id == experiment_id).first()
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found in experiment {experiment_id}. Check both IDs and try again.",
        )
    return RunResponse(
        id=run.id,
        experiment_id=run.experiment_id,
        name=run.name,
        hyperparameters=json.loads(run.hyperparameters) if run.hyperparameters else {},
        accuracy=run.accuracy,
        loss=run.loss,
        latency_ms=run.latency_ms,
        notes=run.notes,
        status=run.status,
        created_at=run.created_at,
    )


# --- HTML Routes ---


@router.get("/experiments/{experiment_id}/runs/{run_id}", response_class=HTMLResponse)
def run_detail_page(request: Request, experiment_id: int, run_id: int, db: Session = Depends(get_db)):
    """Render the run detail page with hyperparameters and metrics."""
    run = db.query(Run).filter(Run.id == run_id, Run.experiment_id == experiment_id).first()
    if not run:
        raise HTTPException(
            status_code=404,
            detail=f"Run {run_id} not found in experiment {experiment_id}.",
        )
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    hp = json.loads(run.hyperparameters) if run.hyperparameters else {}
    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "experiment": {"id": experiment.id, "name": experiment.name},
            "run": {
                "id": run.id,
                "name": run.name or f"Run #{run.id}",
                "hyperparameters": hp,
                "hyperparameters_str": json.dumps(hp, indent=2),
                "accuracy": run.accuracy,
                "accuracy_fmt": f"{run.accuracy:.4f}" if run.accuracy else "N/A",
                "loss": run.loss,
                "loss_fmt": f"{run.loss:.4f}" if run.loss else "N/A",
                "latency_ms": run.latency_ms,
                "latency_fmt": f"{run.latency_ms:.1f}ms" if run.latency_ms else "N/A",
                "status": run.status.value,
                "notes": run.notes,
                "created_at": _format_dt(run.created_at),
            },
        },
    )


@router.get("/experiments/{experiment_id}/compare", response_class=HTMLResponse)
def compare_runs_page(request: Request, experiment_id: int, db: Session = Depends(get_db)):
    """Render the run comparison page with side-by-side metrics and charts."""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found.",
        )
    runs_data = []
    for run in experiment.runs:
        hp = json.loads(run.hyperparameters) if run.hyperparameters else {}
        runs_data.append(
            {
                "id": run.id,
                "name": run.name or f"Run #{run.id}",
                "hyperparameters": hp,
                "accuracy": run.accuracy,
                "accuracy_fmt": f"{run.accuracy:.4f}" if run.accuracy else "N/A",
                "loss": run.loss,
                "loss_fmt": f"{run.loss:.4f}" if run.loss else "N/A",
                "latency_ms": run.latency_ms,
                "latency_fmt": f"{run.latency_ms:.1f}ms" if run.latency_ms else "N/A",
                "status": run.status.value,
                "created_at": _format_dt(run.created_at),
            }
        )

    all_hp_keys = set()
    for r in runs_data:
        all_hp_keys.update(r["hyperparameters"].keys())
    all_hp_keys = sorted(all_hp_keys)

    return templates.TemplateResponse(
        "compare.html",
        {
            "request": request,
            "experiment": {"id": experiment.id, "name": experiment.name},
            "runs": runs_data,
            "hp_keys": all_hp_keys,
            "run_labels": json.dumps([r["name"] for r in runs_data]),
            "run_accuracies": json.dumps([r["accuracy"] for r in runs_data]),
            "run_losses": json.dumps([r["loss"] for r in runs_data]),
            "run_latencies": json.dumps([r["latency_ms"] for r in runs_data]),
        },
    )

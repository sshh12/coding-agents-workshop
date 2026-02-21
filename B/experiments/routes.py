# experiments/routes.py
# API and HTML routes for experiment CRUD.
# Why: Co-locates all experiment endpoints; agents find them by folder name.
# Relevant files: experiments/models.py, experiments/schemas.py, experiments/templates/

from __future__ import annotations

import json
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from experiments.models import Experiment, ExperimentStatus
from experiments.schemas import ExperimentCreate, ExperimentResponse
from runs.models import Run
from shared.db import get_db

router = APIRouter()

_template_dir = os.path.join(os.path.dirname(__file__), "templates")
_shared_template_dir = os.path.join(os.path.dirname(__file__), "..", "shared", "templates")
templates = Jinja2Templates(directory=[_template_dir, _shared_template_dir])


def _format_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else ""


def _experiment_stats(experiment: Experiment):
    runs = experiment.runs
    if not runs:
        return {"total_runs": 0, "avg_accuracy": None, "best_accuracy": None, "avg_loss": None}
    accuracies = [r.accuracy for r in runs if r.accuracy is not None]
    losses = [r.loss for r in runs if r.loss is not None]
    return {
        "total_runs": len(runs),
        "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
        "best_accuracy": max(accuracies) if accuracies else None,
        "avg_loss": sum(losses) / len(losses) if losses else None,
    }


def _status_badge(status: ExperimentStatus) -> str:
    colors = {
        ExperimentStatus.DRAFT: "#6c757d",
        ExperimentStatus.RUNNING: "#0d6efd",
        ExperimentStatus.COMPLETED: "#198754",
        ExperimentStatus.FAILED: "#dc3545",
        ExperimentStatus.ARCHIVED: "#6c757d",
    }
    color = colors.get(status, "#6c757d")
    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{status.value}</span>'


# --- API Routes ---


@router.get("/api/experiments", response_model=list[ExperimentResponse])
def list_experiments(db: Session = Depends(get_db)):
    """List all experiments, newest first."""
    experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
    result = []
    for exp in experiments:
        stats = _experiment_stats(exp)
        result.append(
            ExperimentResponse(
                id=exp.id,
                name=exp.name,
                description=exp.description,
                status=exp.status,
                created_at=exp.created_at,
                updated_at=exp.updated_at,
                total_runs=stats["total_runs"],
                avg_accuracy=stats["avg_accuracy"],
            )
        )
    return result


@router.post("/api/experiments", response_model=ExperimentResponse, status_code=201)
def create_experiment(payload: ExperimentCreate, db: Session = Depends(get_db)):
    """Create a new experiment.

    Returns 201 on success. Validates name is non-empty and status is a valid enum value.
    """
    experiment = Experiment(
        name=payload.name,
        description=payload.description,
        status=payload.status,
    )
    db.add(experiment)
    db.commit()
    db.refresh(experiment)
    return ExperimentResponse(
        id=experiment.id,
        name=experiment.name,
        description=experiment.description,
        status=experiment.status,
        created_at=experiment.created_at,
        updated_at=experiment.updated_at,
    )


@router.get("/api/experiments/{experiment_id}")
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    """Get experiment details including all runs.

    Returns 404 with a message if the experiment does not exist.
    """
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found. Check the ID and try again.",
        )
    runs = []
    for run in experiment.runs:
        hp = json.loads(run.hyperparameters) if run.hyperparameters else {}
        runs.append(
            {
                "id": run.id,
                "name": run.name,
                "hyperparameters": hp,
                "accuracy": run.accuracy,
                "loss": run.loss,
                "latency_ms": run.latency_ms,
                "notes": run.notes,
                "status": run.status.value,
                "created_at": _format_dt(run.created_at),
            }
        )
    stats = _experiment_stats(experiment)
    return {
        "id": experiment.id,
        "name": experiment.name,
        "description": experiment.description,
        "status": experiment.status.value,
        "created_at": _format_dt(experiment.created_at),
        "updated_at": _format_dt(experiment.updated_at),
        "runs": runs,
        **stats,
    }


# --- HTML Routes ---


@router.get("/experiments/{experiment_id}", response_class=HTMLResponse)
def experiment_detail_page(request: Request, experiment_id: int, db: Session = Depends(get_db)):
    """Render the experiment detail page with runs table and metrics charts."""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment {experiment_id} not found. Check the ID and try again.",
        )
    runs_data = []
    for run in experiment.runs:
        hp = json.loads(run.hyperparameters) if run.hyperparameters else {}
        runs_data.append(
            {
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
                "status": run.status,
                "status_badge": _status_badge(ExperimentStatus(run.status.value) if hasattr(run.status, "value") else ExperimentStatus.COMPLETED),
                "notes": run.notes,
                "created_at": _format_dt(run.created_at),
            }
        )

    run_labels = [r["name"] for r in runs_data]
    run_accuracies = [r["accuracy"] for r in runs_data]
    run_losses = [r["loss"] for r in runs_data]

    stats = _experiment_stats(experiment)
    return templates.TemplateResponse(
        "detail.html",
        {
            "request": request,
            "experiment": {
                "id": experiment.id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status,
                "status_badge": _status_badge(experiment.status),
                "created_at": _format_dt(experiment.created_at),
                "updated_at": _format_dt(experiment.updated_at),
            },
            "runs": runs_data,
            "stats": stats,
            "run_labels": json.dumps(run_labels),
            "run_accuracies": json.dumps(run_accuracies),
            "run_losses": json.dumps(run_losses),
        },
    )

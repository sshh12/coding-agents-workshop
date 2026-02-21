#!/usr/bin/env python3
# manage.py
# CLI entrypoint for the ML Experiment Tracker.
# Why: Single command interface so agents (and humans) always know where to start.
# Relevant files: shared/config.py, shared/db.py, experiments/routes.py, runs/routes.py

import argparse
import json
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from shared.base import Base
from shared.config import HOST, PORT
from shared.db import SessionLocal, engine, get_db


def create_app() -> FastAPI:
    """Build and return the FastAPI application with all routes mounted."""

    @asynccontextmanager
    async def lifespan(app):
        Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(title="ML Experiment Tracker", lifespan=lifespan)

    # Import routes after app creation to avoid circular imports
    from experiments.routes import router as experiments_router
    from runs.routes import router as runs_router

    app.include_router(experiments_router)
    app.include_router(runs_router)

    from exports.routes import router as exports_router
    from tags.routes import router as tags_router

    app.include_router(tags_router)
    app.include_router(exports_router)

    # Dashboard
    import os

    _shared_template_dir = os.path.join(os.path.dirname(__file__), "shared", "templates")
    templates = Jinja2Templates(directory=[_shared_template_dir])

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request, db: Session = Depends(get_db)):
        """Render the main dashboard with experiment overview and activity feed."""
        from experiments.models import Experiment

        experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
        exp_data = []
        recent_activity = []
        for exp in experiments:
            runs = exp.runs
            accuracies = [r.accuracy for r in runs if r.accuracy is not None]
            losses = [r.loss for r in runs if r.loss is not None]
            stats = {
                "total_runs": len(runs),
                "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else None,
                "best_accuracy": max(accuracies) if accuracies else None,
                "avg_loss": sum(losses) / len(losses) if losses else None,
            }
            status_colors = {
                "draft": "#6c757d",
                "running": "#0d6efd",
                "completed": "#198754",
                "failed": "#dc3545",
                "archived": "#6c757d",
            }
            status_val = exp.status.value if hasattr(exp.status, "value") else str(exp.status)
            color = status_colors.get(status_val, "#6c757d")
            badge = f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{status_val}</span>'

            desc = exp.description or ""
            if len(desc) > 100:
                desc = desc[:100] + "..."
            fmt_dt = lambda dt: dt.strftime("%Y-%m-%d %H:%M") if dt else ""

            exp_data.append(
                {
                    "id": exp.id,
                    "name": exp.name,
                    "description": desc,
                    "status": status_val,
                    "status_badge": badge,
                    "created_at": fmt_dt(exp.created_at),
                    "total_runs": stats["total_runs"],
                    "avg_accuracy": f"{stats['avg_accuracy']:.4f}" if stats["avg_accuracy"] else "N/A",
                    "best_accuracy": f"{stats['best_accuracy']:.4f}" if stats["best_accuracy"] else "N/A",
                }
            )
            for run in runs[-3:]:
                recent_activity.append(
                    {
                        "type": "run",
                        "experiment_name": exp.name,
                        "experiment_id": exp.id,
                        "run_name": run.name or f"Run #{run.id}",
                        "accuracy": f"{run.accuracy:.4f}" if run.accuracy else "N/A",
                        "created_at": fmt_dt(run.created_at),
                    }
                )

        recent_activity.sort(key=lambda x: x["created_at"], reverse=True)
        recent_activity = recent_activity[:10]

        chart_labels = []
        chart_accuracy = []
        chart_loss = []
        for exp in experiments[:10]:
            accuracies = [r.accuracy for r in exp.runs if r.accuracy is not None]
            losses = [r.loss for r in exp.runs if r.loss is not None]
            name = exp.name
            if len(name) > 20:
                name = name[:20] + "..."
            chart_labels.append(name)
            chart_accuracy.append(sum(accuracies) / len(accuracies) if accuracies else None)
            chart_loss.append(sum(losses) / len(losses) if losses else None)

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "experiments": exp_data,
                "recent_activity": recent_activity,
                "chart_labels": json.dumps(chart_labels),
                "chart_accuracy": json.dumps(chart_accuracy),
                "chart_loss": json.dumps(chart_loss),
                "total_experiments": len(experiments),
                "total_runs": sum(e["total_runs"] for e in exp_data),
            },
        )

    # Health check
    @app.get("/api/health")
    def health():
        """Health check endpoint. Returns 200 if the service is running."""
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    return app


def _ensure_tables():
    """Import all models so Base.metadata knows about them, then create tables."""
    import experiments.models  # noqa: F401
    import exports.models  # noqa: F401
    import runs.models  # noqa: F401
    import tags.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def cmd_run(args):
    """Start the development server."""
    import uvicorn

    _ensure_tables()
    _seed_if_empty()
    print(f"Starting server at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    uvicorn.run(create_app(), host=HOST, port=PORT)


def cmd_seed(args):
    """Load sample experiment data into the database."""
    _ensure_tables()
    _seed_if_empty()


def cmd_migrate(args):
    """Create or update database tables."""
    _ensure_tables()
    print("Database tables created/updated.")


def cmd_check(args):
    """Run ruff lint and pytest."""
    import subprocess

    print("Running ruff check...")
    ruff_result = subprocess.run(["ruff", "check", "."], cwd=sys.path[0] or ".")
    print()
    print("Running pytest...")
    pytest_result = subprocess.run(["pytest"], cwd=sys.path[0] or ".")
    if ruff_result.returncode != 0 or pytest_result.returncode != 0:
        print("\nSome checks failed. Fix the issues above and run again.")
        sys.exit(1)
    print("\nAll checks passed.")


def _seed_if_empty():
    """Insert sample data if the database is empty."""
    from experiments.models import Experiment, ExperimentStatus
    from runs.models import Run, RunStatus

    db = SessionLocal()
    try:
        if db.query(Experiment).count() > 0:
            print("Database already has data, skipping seed.")
            return
        exp1 = Experiment(
            name="BERT Fine-tuning",
            description="Fine-tuning BERT for sentiment analysis on product reviews",
            status=ExperimentStatus.COMPLETED,
        )
        exp2 = Experiment(
            name="GPT-2 Text Generation",
            description="Text generation experiments with various temperature settings",
            status=ExperimentStatus.RUNNING,
        )
        exp3 = Experiment(
            name="ResNet Image Classification",
            description="Image classification on CIFAR-10 with different architectures",
            status=ExperimentStatus.DRAFT,
        )
        db.add_all([exp1, exp2, exp3])
        db.commit()
        db.refresh(exp1)
        db.refresh(exp2)
        db.refresh(exp3)

        runs = [
            Run(
                experiment_id=exp1.id,
                name="lr=2e-5, epochs=3",
                hyperparameters='{"learning_rate": 2e-5, "epochs": 3, "batch_size": 16}',
                accuracy=0.891,
                loss=0.312,
                latency_ms=45.2,
                status=RunStatus.COMPLETED,
            ),
            Run(
                experiment_id=exp1.id,
                name="lr=5e-5, epochs=5",
                hyperparameters='{"learning_rate": 5e-5, "epochs": 5, "batch_size": 32}',
                accuracy=0.923,
                loss=0.245,
                latency_ms=42.8,
                status=RunStatus.COMPLETED,
            ),
            Run(
                experiment_id=exp1.id,
                name="lr=1e-4, epochs=3",
                hyperparameters='{"learning_rate": 1e-4, "epochs": 3, "batch_size": 16}',
                accuracy=0.867,
                loss=0.389,
                latency_ms=44.1,
                status=RunStatus.COMPLETED,
            ),
            Run(
                experiment_id=exp2.id,
                name="temp=0.7",
                hyperparameters='{"temperature": 0.7, "max_tokens": 512, "top_p": 0.9}',
                accuracy=None,
                loss=2.341,
                latency_ms=156.3,
                status=RunStatus.COMPLETED,
            ),
            Run(
                experiment_id=exp2.id,
                name="temp=1.0",
                hyperparameters='{"temperature": 1.0, "max_tokens": 512, "top_p": 0.95}',
                accuracy=None,
                loss=2.567,
                latency_ms=162.1,
                status=RunStatus.COMPLETED,
            ),
            Run(
                experiment_id=exp2.id,
                name="temp=0.3",
                hyperparameters='{"temperature": 0.3, "max_tokens": 256, "top_p": 0.8}',
                accuracy=None,
                loss=2.102,
                latency_ms=89.4,
                status=RunStatus.RUNNING,
            ),
        ]
        db.add_all(runs)
        db.commit()
        print("Sample data seeded successfully.")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="ML Experiment Tracker CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("run", help="Start the development server on port 8000")
    subparsers.add_parser("seed", help="Load sample experiment data")
    subparsers.add_parser("migrate", help="Create or update database tables")
    subparsers.add_parser("check", help="Run ruff lint and pytest")

    args = parser.parse_args()

    commands = {
        "run": cmd_run,
        "seed": cmd_seed,
        "migrate": cmd_migrate,
        "check": cmd_check,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        print("\nAvailable commands: run, seed, migrate, check")
        print("Example: python manage.py run")
        sys.exit(1)


if __name__ == "__main__":
    main()

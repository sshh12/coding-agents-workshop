#!/usr/bin/env python3
"""ML Experiment Tracker - main app file"""

import os
import json
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# ============================================================
# Database setup
# ============================================================

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================
# Models (all in this file because it's easier)
# ============================================================

class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="draft")  # draft, running, completed, failed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True, index=True)
    experiment_id = Column(Integer, ForeignKey("experiments.id"), nullable=False)
    name = Column(String, default="")
    hyperparameters = Column(Text, default="{}")  # JSON string
    accuracy = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)
    notes = Column(Text, default="")
    status = Column(String, default="completed")  # running, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    experiment = relationship("Experiment", back_populates="runs")


# ============================================================
# Create tables
# ============================================================

Base.metadata.create_all(bind=engine)

# ============================================================
# Template helpers
# ============================================================

from h import fmt, do_thing, proc_data, mk_resp, chk, trunc

def get_db():
    db = SessionLocal()
    try:
        return db
    except:
        pass

def close_db(db):
    try:
        db.close()
    except:
        pass

def get_status_color(status):
    colors = {
        "draft": "#6c757d",
        "running": "#0d6efd",
        "completed": "#198754",
        "failed": "#dc3545",
        "archived": "#6c757d",
    }
    try:
        return colors[status]
    except:
        return "#6c757d"

def get_status_badge(status):
    color = get_status_color(status)
    return f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;">{status}</span>'

def parse_hyperparams(hp_string):
    try:
        return json.loads(hp_string)
    except:
        return {}

def calc_experiment_stats(experiment, db):
    try:
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
    except:
        return {"total_runs": 0, "avg_accuracy": None, "best_accuracy": None, "avg_loss": None}

# ============================================================
# App setup
# ============================================================

@asynccontextmanager
async def lifespan(app):
    # startup
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown

app = FastAPI(title="ML Experiment Tracker", lifespan=lifespan)
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "stuff", "templates"))

# ============================================================
# Dashboard route
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = get_db()
    try:
        experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
        exp_data = []
        recent_activity = []
        for exp in experiments:
            stats = calc_experiment_stats(exp, db)
            exp_data.append({
                "id": exp.id,
                "name": exp.name,
                "description": trunc(exp.description, 100),
                "status": exp.status,
                "status_badge": get_status_badge(exp.status),
                "created_at": fmt(exp.created_at),
                "total_runs": stats["total_runs"],
                "avg_accuracy": f"{stats['avg_accuracy']:.4f}" if stats["avg_accuracy"] else "N/A",
                "best_accuracy": f"{stats['best_accuracy']:.4f}" if stats["best_accuracy"] else "N/A",
            })
            for run in exp.runs[-3:]:
                recent_activity.append({
                    "type": "run",
                    "experiment_name": exp.name,
                    "experiment_id": exp.id,
                    "run_name": run.name or f"Run #{run.id}",
                    "accuracy": f"{run.accuracy:.4f}" if run.accuracy else "N/A",
                    "created_at": fmt(run.created_at),
                })
        recent_activity.sort(key=lambda x: x["created_at"], reverse=True)
        recent_activity = recent_activity[:10]

        # calculate chart data
        chart_labels = []
        chart_accuracy = []
        chart_loss = []
        for exp in experiments[:10]:
            stats = calc_experiment_stats(exp, db)
            chart_labels.append(trunc(exp.name, 20))
            chart_accuracy.append(stats["avg_accuracy"])
            chart_loss.append(stats["avg_loss"])

        close_db(db)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "experiments": exp_data,
            "recent_activity": recent_activity,
            "chart_labels": json.dumps(chart_labels),
            "chart_accuracy": json.dumps(chart_accuracy),
            "chart_loss": json.dumps(chart_loss),
            "total_experiments": len(experiments),
            "total_runs": sum(e["total_runs"] for e in exp_data),
        })
    except Exception as e:
        close_db(db)
        try:
            return templates.TemplateResponse("index.html", {
                "request": request,
                "experiments": [],
                "recent_activity": [],
                "chart_labels": "[]",
                "chart_accuracy": "[]",
                "chart_loss": "[]",
                "total_experiments": 0,
                "total_runs": 0,
            })
        except:
            return HTMLResponse("<h1>Dashboard Error</h1>")

# ============================================================
# Experiment detail page
# ============================================================

@app.get("/experiments/{experiment_id}", response_class=HTMLResponse)
async def experiment_detail(request: Request, experiment_id: int):
    db = get_db()
    try:
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            close_db(db)
            raise HTTPException(status_code=404)
        runs_data = []
        for run in experiment.runs:
            hp = parse_hyperparams(run.hyperparameters)
            runs_data.append({
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
                "status_badge": get_status_badge(run.status),
                "notes": run.notes,
                "created_at": fmt(run.created_at),
            })

        # chart data for this experiment
        run_labels = [r["name"] for r in runs_data]
        run_accuracies = [r["accuracy"] for r in runs_data]
        run_losses = [r["loss"] for r in runs_data]
        run_latencies = [r["latency_ms"] for r in runs_data]

        stats = calc_experiment_stats(experiment, db)
        close_db(db)
        return templates.TemplateResponse("experiment.html", {
            "request": request,
            "experiment": {
                "id": experiment.id,
                "name": experiment.name,
                "description": experiment.description,
                "status": experiment.status,
                "status_badge": get_status_badge(experiment.status),
                "created_at": fmt(experiment.created_at),
                "updated_at": fmt(experiment.updated_at),
            },
            "runs": runs_data,
            "stats": stats,
            "run_labels": json.dumps(run_labels),
            "run_accuracies": json.dumps(run_accuracies),
            "run_losses": json.dumps(run_losses),
            "run_latencies": json.dumps(run_latencies),
        })
    except HTTPException:
        raise
    except:
        close_db(db)
        return HTMLResponse("<h1>Error loading experiment</h1>")

# ============================================================
# Compare runs page
# ============================================================

@app.get("/experiments/{experiment_id}/compare", response_class=HTMLResponse)
async def compare_runs(request: Request, experiment_id: int):
    db = get_db()
    try:
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            close_db(db)
            raise HTTPException(status_code=404)
        runs_data = []
        for run in experiment.runs:
            hp = parse_hyperparams(run.hyperparameters)
            runs_data.append({
                "id": run.id,
                "name": run.name or f"Run #{run.id}",
                "hyperparameters": hp,
                "accuracy": run.accuracy,
                "accuracy_fmt": f"{run.accuracy:.4f}" if run.accuracy else "N/A",
                "loss": run.loss,
                "loss_fmt": f"{run.loss:.4f}" if run.loss else "N/A",
                "latency_ms": run.latency_ms,
                "latency_fmt": f"{run.latency_ms:.1f}ms" if run.latency_ms else "N/A",
                "status": run.status,
                "created_at": fmt(run.created_at),
            })
        # collect all hyperparameter keys
        all_hp_keys = set()
        for r in runs_data:
            all_hp_keys.update(r["hyperparameters"].keys())
        all_hp_keys = sorted(all_hp_keys)

        close_db(db)
        return templates.TemplateResponse("compare.html", {
            "request": request,
            "experiment": {"id": experiment.id, "name": experiment.name},
            "runs": runs_data,
            "hp_keys": all_hp_keys,
            "run_labels": json.dumps([r["name"] for r in runs_data]),
            "run_accuracies": json.dumps([r["accuracy"] for r in runs_data]),
            "run_losses": json.dumps([r["loss"] for r in runs_data]),
            "run_latencies": json.dumps([r["latency_ms"] for r in runs_data]),
        })
    except HTTPException:
        raise
    except:
        close_db(db)
        return HTMLResponse("<h1>Error comparing runs</h1>")

# ============================================================
# API: List experiments
# ============================================================

@app.get("/api/experiments")
async def list_experiments():
    db = get_db()
    try:
        experiments = db.query(Experiment).order_by(Experiment.created_at.desc()).all()
        result = []
        for exp in experiments:
            stats = calc_experiment_stats(exp, db)
            result.append({
                "id": exp.id,
                "name": exp.name,
                "description": exp.description,
                "status": exp.status,
                "created_at": fmt(exp.created_at),
                "updated_at": fmt(exp.updated_at),
                "total_runs": stats["total_runs"],
                "avg_accuracy": stats["avg_accuracy"],
            })
        close_db(db)
        return result
    except:
        close_db(db)
        return []

# ============================================================
# API: Create experiment
# ============================================================

@app.post("/api/experiments")
async def create_experiment(request: Request):
    db = get_db()
    try:
        body = await request.json()
        name = body.get("name")
        if not name:
            close_db(db)
            return JSONResponse({"error": "name required"}, status_code=400)
        description = body.get("description", "")
        status = body.get("status", "draft")
        # no validation on status, just accept whatever
        exp = Experiment(name=name, description=description, status=status)
        db.add(exp)
        db.commit()
        db.refresh(exp)
        result = {
            "id": exp.id,
            "name": exp.name,
            "description": exp.description,
            "status": exp.status,
            "created_at": fmt(exp.created_at),
        }
        close_db(db)
        return result
    except:
        close_db(db)
        return JSONResponse({"error": "something went wrong"}, status_code=500)

# ============================================================
# API: Get experiment
# ============================================================

@app.get("/api/experiments/{experiment_id}")
async def get_experiment(experiment_id: int):
    db = get_db()
    try:
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            close_db(db)
            return JSONResponse({"error": "not found"}, status_code=404)
        runs = []
        for run in experiment.runs:
            runs.append({
                "id": run.id,
                "name": run.name,
                "hyperparameters": do_thing(run.hyperparameters),
                "accuracy": run.accuracy,
                "loss": run.loss,
                "latency_ms": run.latency_ms,
                "notes": run.notes,
                "status": run.status,
                "created_at": fmt(run.created_at),
            })
        result = {
            "id": experiment.id,
            "name": experiment.name,
            "description": experiment.description,
            "status": experiment.status,
            "created_at": fmt(experiment.created_at),
            "updated_at": fmt(experiment.updated_at),
            "runs": runs,
        }
        close_db(db)
        return result
    except:
        close_db(db)
        return JSONResponse({"error": "something went wrong"}, status_code=500)

# ============================================================
# API: Create run
# ============================================================

@app.post("/api/experiments/{experiment_id}/runs")
async def create_run(experiment_id: int, request: Request):
    db = get_db()
    try:
        experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
        if not experiment:
            close_db(db)
            return JSONResponse({"error": "not found"}, status_code=404)
        body = await request.json()
        name = body.get("name", "")
        hyperparameters = body.get("hyperparameters", {})
        if isinstance(hyperparameters, dict):
            hyperparameters = json.dumps(hyperparameters)
        accuracy = body.get("accuracy")
        loss = body.get("loss")
        latency_ms = body.get("latency_ms")
        notes = body.get("notes", "")
        status = body.get("status", "completed")
        run = Run(
            experiment_id=experiment_id,
            name=name,
            hyperparameters=hyperparameters,
            accuracy=accuracy,
            loss=loss,
            latency_ms=latency_ms,
            notes=notes,
            status=status,
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        result = {
            "id": run.id,
            "experiment_id": run.experiment_id,
            "name": run.name,
            "accuracy": run.accuracy,
            "loss": run.loss,
            "latency_ms": run.latency_ms,
            "status": run.status,
            "created_at": fmt(run.created_at),
        }
        close_db(db)
        return result
    except:
        close_db(db)
        return JSONResponse({"error": "something went wrong"}, status_code=500)

# ============================================================
# API: Get run details
# ============================================================

@app.get("/api/experiments/{experiment_id}/runs/{run_id}")
async def get_run(experiment_id: int, run_id: int):
    db = get_db()
    try:
        run = db.query(Run).filter(Run.id == run_id, Run.experiment_id == experiment_id).first()
        if not run:
            close_db(db)
            return JSONResponse({"error": "not found"}, status_code=404)
        result = {
            "id": run.id,
            "experiment_id": run.experiment_id,
            "name": run.name,
            "hyperparameters": do_thing(run.hyperparameters),
            "accuracy": run.accuracy,
            "loss": run.loss,
            "latency_ms": run.latency_ms,
            "notes": run.notes,
            "status": run.status,
            "created_at": fmt(run.created_at),
        }
        close_db(db)
        return result
    except:
        close_db(db)
        return JSONResponse({"error": "something went wrong"}, status_code=500)

# ============================================================
# Health check
# ============================================================

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": fmt(datetime.utcnow())}

# ============================================================
# Seed data helper (not an API, just call from shell)
# ============================================================

def seed():
    db = SessionLocal()
    try:
        # check if data exists
        if db.query(Experiment).count() > 0:
            print("Data already exists")
            return
        # create experiments
        exp1 = Experiment(name="BERT Fine-tuning", description="Fine-tuning BERT for sentiment analysis on product reviews", status="completed")
        exp2 = Experiment(name="GPT-2 Text Generation", description="Text generation experiments with various temperature settings", status="running")
        exp3 = Experiment(name="ResNet Image Classification", description="Image classification on CIFAR-10 with different architectures", status="draft")
        db.add_all([exp1, exp2, exp3])
        db.commit()
        db.refresh(exp1)
        db.refresh(exp2)
        db.refresh(exp3)
        # add runs
        runs = [
            Run(experiment_id=exp1.id, name="lr=2e-5, epochs=3", hyperparameters='{"learning_rate": 2e-5, "epochs": 3, "batch_size": 16}', accuracy=0.891, loss=0.312, latency_ms=45.2, status="completed"),
            Run(experiment_id=exp1.id, name="lr=5e-5, epochs=5", hyperparameters='{"learning_rate": 5e-5, "epochs": 5, "batch_size": 32}', accuracy=0.923, loss=0.245, latency_ms=42.8, status="completed"),
            Run(experiment_id=exp1.id, name="lr=1e-4, epochs=3", hyperparameters='{"learning_rate": 1e-4, "epochs": 3, "batch_size": 16}', accuracy=0.867, loss=0.389, latency_ms=44.1, status="completed"),
            Run(experiment_id=exp2.id, name="temp=0.7", hyperparameters='{"temperature": 0.7, "max_tokens": 512, "top_p": 0.9}', accuracy=None, loss=2.341, latency_ms=156.3, status="completed"),
            Run(experiment_id=exp2.id, name="temp=1.0", hyperparameters='{"temperature": 1.0, "max_tokens": 512, "top_p": 0.95}', accuracy=None, loss=2.567, latency_ms=162.1, status="completed"),
            Run(experiment_id=exp2.id, name="temp=0.3", hyperparameters='{"temperature": 0.3, "max_tokens": 256, "top_p": 0.8}', accuracy=None, loss=2.102, latency_ms=89.4, status="running"),
        ]
        db.add_all(runs)
        db.commit()
        print("Seed data created")
    except:
        pass
    finally:
        db.close()

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed()
    else:
        seed()  # always seed on startup
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)

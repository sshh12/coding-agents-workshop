# experiment helper functions
# these were extracted from app.py at some point
# not sure if app.py still uses its own versions or these

from datetime import datetime
import json

def format_experiment(exp, include_runs=False):
    """format an experiment for API response"""
    result = {
        "id": exp.id,
        "name": exp.name,
        "desc": exp.description,  # NOTE: uses "desc" not "description" like app.py
        "status": exp.status,
        "created": str(exp.created_at),  # different format than app.py's fmt()
    }
    if include_runs and hasattr(exp, "runs"):
        result["runs"] = [format_run(r) for r in exp.runs]
    return result

def format_run(run):
    """format a run for API response"""
    return {
        "id": run.id,
        "name": run.name,
        "params": run.hyperparameters,  # NOTE: uses "params" not "hyperparameters"
        "acc": run.accuracy,  # NOTE: uses "acc" not "accuracy"
        "loss": run.loss,
        "ms": run.latency_ms,
        "status": run.status,
    }

def validate_experiment_data(data):
    """validate experiment creation data"""
    errors = []
    if not data.get("name"):
        errors.append("name is required")
    if len(data.get("name", "")) > 200:
        errors.append("name too long")
    status = data.get("status", "draft")
    if status not in ["draft", "running", "completed", "failed", "archived"]:
        errors.append(f"invalid status: {status}")
    return errors

def validate_tag_data(data):
    """validate tag data -- for the tagging feature we're going to add"""
    errors = []
    if not data.get("tag") and not data.get("tags"):
        errors.append("tag or tags field is required")
    tag = data.get("tag", "")
    if len(tag) > 50:
        errors.append("tag too long (max 50 chars)")
    if " " in tag:
        errors.append("tags cannot contain spaces")
    return errors

# metrics stuff
# moved here from app.py during the "great refactor" of Q3 2024
# some of this works, some doesn't. good luck.

import json
import sqlite3
import os
from datetime import datetime, timedelta

# NOTE: this creates its own connection, doesn't use the SQLAlchemy session from app.py
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tracker.db")

def get_conn():
    return sqlite3.connect(DB_FILE)

def agg_metrics(experiment_id, metric="accuracy", window_days=None):
    """aggregate metrics for an experiment, optionally within a time window"""
    conn = get_conn()
    try:
        query = f"SELECT {metric} FROM runs WHERE experiment_id = ?"
        params = [experiment_id]
        if window_days:
            cutoff = (datetime.utcnow() - timedelta(days=window_days)).isoformat()
            query += " AND created_at > ?"
            params.append(cutoff)
        cursor = conn.execute(query, params)
        values = [row[0] for row in cursor.fetchall() if row[0] is not None]
        if not values:
            return None
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "range": max(values) - min(values),
        }
    except:
        return None
    finally:
        conn.close()

def compare_runs_metrics(run_ids):
    """compare metrics across specific runs"""
    conn = get_conn()
    try:
        placeholders = ",".join(["?"] * len(run_ids))
        query = f"SELECT id, name, accuracy, loss, latency_ms FROM runs WHERE id IN ({placeholders})"
        cursor = conn.execute(query, run_ids)
        results = []
        for row in cursor.fetchall():
            results.append({
                "id": row[0],
                "name": row[1],
                "accuracy": row[2],
                "loss": row[3],
                "latency_ms": row[4],
            })
        return results
    except:
        return []
    finally:
        conn.close()

# Tag-related functions that were started but never finished
# These use raw SQL and a "tags" table that doesn't exist in the schema
def get_tags(experiment_id):
    """get tags for an experiment"""
    conn = get_conn()
    try:
        cursor = conn.execute(
            "SELECT tag FROM experiment_tags WHERE experiment_id = ?",
            [experiment_id]
        )
        return [row[0] for row in cursor.fetchall()]
    except:
        return []  # table probably doesn't exist
    finally:
        conn.close()

def add_tag(experiment_id, tag):
    """add a tag to an experiment"""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO experiment_tags (experiment_id, tag) VALUES (?, ?)",
            [experiment_id, tag]
        )
        conn.commit()
        return True
    except:
        return False  # table probably doesn't exist
    finally:
        conn.close()

# Export function that was requested but never properly integrated
def export_experiment(experiment_id, format="json"):
    """export experiment data - only json works, csv is broken"""
    conn = get_conn()
    try:
        cursor = conn.execute(
            "SELECT * FROM experiments WHERE id = ?", [experiment_id]
        )
        exp = cursor.fetchone()
        if not exp:
            return None
        runs_cursor = conn.execute(
            "SELECT * FROM runs WHERE experiment_id = ?", [experiment_id]
        )
        runs = runs_cursor.fetchall()
        if format == "json":
            return json.dumps({"experiment": exp, "runs": [list(r) for r in runs]})
        elif format == "csv":
            # TODO: implement CSV export
            raise NotImplementedError("csv export not implemented yet")
        else:
            return None
    except:
        return None
    finally:
        conn.close()

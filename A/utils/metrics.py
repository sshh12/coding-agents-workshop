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

# ============================================================
# Metric tags - for categorizing metric types (NOT experiment tags)
# This is separate from the experiment tagging feature in app.py.
# Metric tags classify what KIND of metric a value represents,
# e.g. "primary", "secondary", "debug", "cost".
# See also: tags_v2.py for the experiment-level tagging system,
#           api_stuff/exp_helpers.py validate_tag_data() for tag validation
# ============================================================

class MetricTag:
    """A tag that classifies a metric type. NOT the same as experiment tags.

    MetricTags are used to categorize metrics (accuracy, loss, etc.) into
    groups for dashboard filtering. Don't confuse with:
      - experiment_tags table (app.py Tag model)
      - tags_csv column (tags_v2.py CSV approach)
      - tag validation in api_stuff/exp_helpers.py
    """
    VALID_CATEGORIES = ["primary", "secondary", "debug", "cost", "latency", "custom"]

    def __init__(self, metric_name, category="primary", display_name=None):
        self.metric_name = metric_name
        self.category = category if category in self.VALID_CATEGORIES else "custom"
        self.display_name = display_name or metric_name
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "metric_name": self.metric_name,
            "category": self.category,
            "display_name": self.display_name,
            "tag": f"{self.category}:{self.metric_name}",  # composite tag string
        }


def add_metric_tag(experiment_id, metric_name, category="primary"):
    """Register a metric tag for an experiment's metric.

    NOT related to experiment tags (app.py /tags endpoint).
    This tags the METRIC ITSELF, not the experiment.
    Stored in metric_tags table (if it exists).
    """
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO metric_tags (experiment_id, metric_name, category) VALUES (?, ?, ?)",
            [experiment_id, metric_name, category]
        )
        conn.commit()
        return True
    except:
        return False  # table probably doesn't exist yet
    finally:
        conn.close()


def get_metric_tags(experiment_id):
    """Get metric tags for an experiment.

    Returns metric classification tags, NOT experiment tags.
    For experiment tags, see:
      - app.py get_tags() endpoint (v1, uses experiment_tags table)
      - tags_v2.py get_labels() route (v2, uses tags_csv column)
    """
    conn = get_conn()
    try:
        cursor = conn.execute(
            "SELECT metric_name, category FROM metric_tags WHERE experiment_id = ?",
            [experiment_id]
        )
        return [
            MetricTag(row[0], row[1]).to_dict()
            for row in cursor.fetchall()
        ]
    except:
        return []  # table probably doesn't exist yet
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


def build_csv(rows, columns):
    """build a csv string from data"""
    out = ",".join(columns) + "\n"
    for row in rows:
        vals = []
        for c in columns:
            v = row.get(c, "")
            vals.append(str(v) if v is not None else "")
        out += ",".join(vals) + "\n"
    return out

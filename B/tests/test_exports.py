# tests/test_exports.py
# Tests for experiment export endpoints.
# Why: Fixed test suite that verifies JSON and CSV export.
# Relevant files: exports/routes.py, exports/models.py, tests/conftest.py

import json


def _create_experiment_with_runs(client):
    """Helper: create an experiment with two runs and return the experiment ID."""
    exp_resp = client.post("/api/experiments", json={"name": "Export Test"})
    exp_id = exp_resp.json()["id"]
    client.post(f"/api/experiments/{exp_id}/runs", json={"name": "R1", "accuracy": 0.9, "loss": 0.1})
    client.post(f"/api/experiments/{exp_id}/runs", json={"name": "R2", "accuracy": 0.85, "loss": 0.2})
    return exp_id


def test_export_json(client):
    """Exporting as JSON returns 201 with valid JSON result."""
    exp_id = _create_experiment_with_runs(client)
    response = client.post(f"/api/experiments/{exp_id}/export", json={"format": "json"})
    assert response.status_code == 201
    data = response.json()
    result = json.loads(data["result"])
    assert result["experiment"]["name"] == "Export Test"
    assert len(result["runs"]) == 2


def test_export_csv(client):
    """Exporting as CSV returns 201 with CSV content."""
    exp_id = _create_experiment_with_runs(client)
    response = client.post(f"/api/experiments/{exp_id}/export", json={"format": "csv"})
    assert response.status_code == 201
    data = response.json()
    assert "accuracy" in data["result"]
    assert "R1" in data["result"]


def test_export_experiment_not_found(client):
    """Exporting a nonexistent experiment returns 404."""
    response = client.post("/api/experiments/999/export", json={"format": "json"})
    assert response.status_code == 404

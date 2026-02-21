# tests/test_runs.py
# Tests for run logging and retrieval endpoints.
# Why: Fixed test suite that verifies run creation, metrics, and experiment association.
# Relevant files: runs/routes.py, runs/models.py, tests/conftest.py


def _create_experiment(client, name="Test Experiment"):
    """Helper: create an experiment and return its ID."""
    resp = client.post("/api/experiments", json={"name": name})
    return resp.json()["id"]


def test_create_run(client):
    """Logging a run returns 201 with metrics data."""
    exp_id = _create_experiment(client)
    response = client.post(
        f"/api/experiments/{exp_id}/runs",
        json={
            "name": "Run 1",
            "hyperparameters": {"lr": 0.001, "epochs": 10},
            "accuracy": 0.95,
            "loss": 0.15,
            "latency_ms": 42.0,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Run 1"
    assert data["accuracy"] == 0.95
    assert data["loss"] == 0.15
    assert data["experiment_id"] == exp_id


def test_create_run_experiment_not_found(client):
    """Logging a run for a nonexistent experiment returns 404."""
    response = client.post(
        "/api/experiments/999/runs",
        json={"name": "Orphan Run"},
    )
    assert response.status_code == 404


def test_create_run_defaults(client):
    """Logging a run with no optional fields uses defaults."""
    exp_id = _create_experiment(client)
    response = client.post(f"/api/experiments/{exp_id}/runs", json={})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "completed"
    assert data["accuracy"] is None
    assert data["hyperparameters"] == {}


def test_get_run(client):
    """Getting a specific run returns its full details."""
    exp_id = _create_experiment(client)
    create_resp = client.post(
        f"/api/experiments/{exp_id}/runs",
        json={"name": "Detail Run", "accuracy": 0.88},
    )
    run_id = create_resp.json()["id"]
    response = client.get(f"/api/experiments/{exp_id}/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Run"
    assert data["accuracy"] == 0.88


def test_get_run_not_found(client):
    """Getting a nonexistent run returns 404."""
    exp_id = _create_experiment(client)
    response = client.get(f"/api/experiments/{exp_id}/runs/999")
    assert response.status_code == 404


def test_experiment_shows_runs(client):
    """Getting an experiment includes its runs."""
    exp_id = _create_experiment(client)
    client.post(f"/api/experiments/{exp_id}/runs", json={"name": "R1", "accuracy": 0.9})
    client.post(f"/api/experiments/{exp_id}/runs", json={"name": "R2", "accuracy": 0.85})
    response = client.get(f"/api/experiments/{exp_id}")
    data = response.json()
    assert len(data["runs"]) == 2
    assert data["total_runs"] == 2

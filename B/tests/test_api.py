# tests/test_api.py
# Integration tests for the full API surface and dashboard.
# Why: Verifies endpoints work together and the dashboard renders.
# Relevant files: manage.py, experiments/routes.py, runs/routes.py


def test_health_check(client):
    """Health endpoint returns 200 with status ok."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_dashboard_renders(client):
    """Dashboard page returns 200 and contains expected content."""
    response = client.get("/")
    assert response.status_code == 200
    assert "ML Experiment Tracker" in response.text


def test_dashboard_with_data(client):
    """Dashboard shows experiment data after creation."""
    client.post("/api/experiments", json={"name": "Dashboard Exp"})
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard Exp" in response.text


def test_compare_page_renders(client):
    """Compare runs page renders for an experiment with runs."""
    exp_resp = client.post("/api/experiments", json={"name": "Compare Test"})
    exp_id = exp_resp.json()["id"]
    client.post(
        f"/api/experiments/{exp_id}/runs",
        json={"name": "R1", "accuracy": 0.9, "loss": 0.1},
    )
    client.post(
        f"/api/experiments/{exp_id}/runs",
        json={"name": "R2", "accuracy": 0.85, "loss": 0.2},
    )
    response = client.get(f"/experiments/{exp_id}/compare")
    assert response.status_code == 200
    assert "Compare Runs" in response.text
    assert "R1" in response.text
    assert "R2" in response.text


def test_full_workflow(client):
    """End-to-end: create experiment, log runs, retrieve, compare."""
    # Create experiment
    exp_resp = client.post(
        "/api/experiments",
        json={"name": "E2E Test", "description": "Full workflow", "status": "running"},
    )
    assert exp_resp.status_code == 201
    exp_id = exp_resp.json()["id"]

    # Log runs
    run1_resp = client.post(
        f"/api/experiments/{exp_id}/runs",
        json={"name": "Baseline", "accuracy": 0.80, "loss": 0.5, "latency_ms": 100.0},
    )
    assert run1_resp.status_code == 201

    run2_resp = client.post(
        f"/api/experiments/{exp_id}/runs",
        json={"name": "Optimized", "accuracy": 0.92, "loss": 0.2, "latency_ms": 50.0},
    )
    assert run2_resp.status_code == 201

    # Retrieve experiment with runs
    detail_resp = client.get(f"/api/experiments/{exp_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert detail["name"] == "E2E Test"
    assert detail["status"] == "running"
    assert len(detail["runs"]) == 2
    assert detail["total_runs"] == 2
    assert detail["best_accuracy"] == 0.92

    # Check individual run
    run_id = run1_resp.json()["id"]
    run_resp = client.get(f"/api/experiments/{exp_id}/runs/{run_id}")
    assert run_resp.status_code == 200
    assert run_resp.json()["name"] == "Baseline"

    # Verify list
    list_resp = client.get("/api/experiments")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

# tests/test_experiments.py
# Tests for experiment CRUD endpoints.
# Why: Fixed test suite that verifies experiment creation, listing, and retrieval.
# Relevant files: experiments/routes.py, experiments/models.py, tests/conftest.py


def test_create_experiment(client):
    """Creating an experiment returns 201 with the experiment data."""
    response = client.post(
        "/api/experiments",
        json={"name": "Test Experiment", "description": "A test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Experiment"
    assert data["description"] == "A test"
    assert data["status"] == "draft"
    assert "id" in data


def test_create_experiment_missing_name(client):
    """Creating an experiment without a name returns 422."""
    response = client.post("/api/experiments", json={"description": "No name"})
    assert response.status_code == 422


def test_create_experiment_invalid_status(client):
    """Creating an experiment with an invalid status returns 422."""
    response = client.post(
        "/api/experiments",
        json={"name": "Test", "status": "nonexistent"},
    )
    assert response.status_code == 422


def test_list_experiments_empty(client):
    """Listing experiments on an empty database returns an empty list."""
    response = client.get("/api/experiments")
    assert response.status_code == 200
    assert response.json() == []


def test_list_experiments(client):
    """Listing experiments returns all created experiments."""
    client.post("/api/experiments", json={"name": "Exp 1"})
    client.post("/api/experiments", json={"name": "Exp 2"})
    response = client.get("/api/experiments")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_experiment(client):
    """Getting a specific experiment returns its details and runs."""
    create_resp = client.post(
        "/api/experiments",
        json={"name": "Detail Test", "description": "Testing detail endpoint"},
    )
    exp_id = create_resp.json()["id"]
    response = client.get(f"/api/experiments/{exp_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Detail Test"
    assert data["runs"] == []


def test_get_experiment_not_found(client):
    """Getting a nonexistent experiment returns 404."""
    response = client.get("/api/experiments/999")
    assert response.status_code == 404


def test_experiment_detail_page(client):
    """The experiment detail HTML page renders successfully."""
    create_resp = client.post("/api/experiments", json={"name": "HTML Test"})
    exp_id = create_resp.json()["id"]
    response = client.get(f"/experiments/{exp_id}")
    assert response.status_code == 200
    assert "HTML Test" in response.text

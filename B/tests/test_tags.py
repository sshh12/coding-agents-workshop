# tests/test_tags.py
# Tests for experiment tagging endpoints.
# Why: Fixed test suite that verifies tag creation, listing, and duplicate handling.
# Relevant files: tags/routes.py, tags/models.py, tests/conftest.py


def _create_experiment(client, name="Test Experiment"):
    """Helper: create an experiment and return its ID."""
    resp = client.post("/api/experiments", json={"name": name})
    return resp.json()["id"]


def test_list_tags_empty(client):
    """Listing tags for an experiment with no tags returns an empty list."""
    exp_id = _create_experiment(client)
    response = client.get(f"/api/experiments/{exp_id}/tags")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tags_experiment_not_found(client):
    """Listing tags for a nonexistent experiment returns 404."""
    response = client.get("/api/experiments/999/tags")
    assert response.status_code == 404


def test_add_tag(client):
    """Adding a tag returns 201 with the tag data."""
    exp_id = _create_experiment(client)
    response = client.post(
        f"/api/experiments/{exp_id}/tags",
        json={"name": "nlp"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "nlp"
    assert data["experiment_id"] == exp_id


def test_add_tag_experiment_not_found(client):
    """Adding a tag to a nonexistent experiment returns 404."""
    response = client.post("/api/experiments/999/tags", json={"name": "test"})
    assert response.status_code == 404


def test_add_duplicate_tag(client):
    """Adding the same tag twice returns 409."""
    exp_id = _create_experiment(client)
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    response = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    assert response.status_code == 409


def test_list_tags_after_adding(client):
    """Listing tags after adding returns all tags."""
    exp_id = _create_experiment(client)
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "production"})
    response = client.get(f"/api/experiments/{exp_id}/tags")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) == 2
    names = {t["name"] for t in tags}
    assert names == {"nlp", "production"}

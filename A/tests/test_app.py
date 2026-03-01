# tests for the app

import os
import sys
import pytest

# ensure the app module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app import app, Base, engine, SessionLocal, Experiment, Tag


@pytest.fixture(autouse=True)
def clean_db():
    """Reset database tables before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_experiment(client):
    """Create a sample experiment and return its data."""
    resp = client.post("/api/experiments", json={"name": "Test Experiment", "description": "A test"})
    assert resp.status_code == 200
    return resp.json()


# ---- Existing functionality tests ----

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_experiment(client):
    resp = client.post("/api/experiments", json={"name": "My Experiment"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "My Experiment"
    assert "id" in data


def test_create_experiment_missing_name(client):
    resp = client.post("/api/experiments", json={"description": "no name"})
    assert resp.status_code == 400


def test_list_experiments(client, sample_experiment):
    resp = client.get("/api/experiments")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_experiment(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.get(f"/api/experiments/{exp_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Experiment"


def test_get_experiment_not_found(client):
    resp = client.get("/api/experiments/9999")
    assert resp.status_code == 404


# ---- Tagging feature tests ----

def test_add_tag(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "nlp"
    assert data["experiment_id"] == exp_id
    assert "id" in data


def test_add_tag_missing_name(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={})
    assert resp.status_code == 400
    assert "name" in resp.json()["error"]


def test_add_tag_empty_name(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "  "})
    assert resp.status_code == 400


def test_add_tag_too_long(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "x" * 51})
    assert resp.status_code == 400
    assert "too long" in resp.json()["error"]


def test_add_tag_experiment_not_found(client):
    resp = client.post("/api/experiments/9999/tags", json={"name": "oops"})
    assert resp.status_code == 404


def test_add_duplicate_tag(client, sample_experiment):
    exp_id = sample_experiment["id"]
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    assert resp.status_code == 409


def test_get_tags(client, sample_experiment):
    exp_id = sample_experiment["id"]
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "nlp"})
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "bert"})
    resp = client.get(f"/api/experiments/{exp_id}/tags")
    assert resp.status_code == 200
    tags = resp.json()
    assert len(tags) == 2
    tag_names = {t["name"] for t in tags}
    assert tag_names == {"nlp", "bert"}


def test_get_tags_empty(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.get(f"/api/experiments/{exp_id}/tags")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_tags_experiment_not_found(client):
    resp = client.get("/api/experiments/9999/tags")
    assert resp.status_code == 404


def test_tags_on_detail_page(client, sample_experiment):
    exp_id = sample_experiment["id"]
    client.post(f"/api/experiments/{exp_id}/tags", json={"name": "vision"})
    resp = client.get(f"/experiments/{exp_id}")
    assert resp.status_code == 200
    assert "vision" in resp.text


def test_add_tag_strips_whitespace(client, sample_experiment):
    exp_id = sample_experiment["id"]
    resp = client.post(f"/api/experiments/{exp_id}/tags", json={"name": "  nlp  "})
    assert resp.status_code == 200
    assert resp.json()["name"] == "nlp"

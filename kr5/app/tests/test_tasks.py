import pytest
from fastapi.testclient import TestClient
from app.main import app, db


@pytest.fixture(autouse=True)
def clean_db():
    db.clear()
    yield
    db.clear()


client = TestClient(app)


def test_create_task_success():
    response = client.post(
        "/tasks",
        json={"title": "Test", "description": "Desc", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test"
    assert data["owner_id"] == 10


def test_create_task_short_title():
    response = client.post(
        "/tasks",
        json={"title": "Te", "priority": 3},
        headers={"X-User-Id": "10"}
    )
    assert response.status_code == 422


def test_create_task_no_user_id():
    response = client.post(
        "/tasks",
        json={"title": "Test", "priority": 3}
    )
    assert response.status_code == 401


def test_get_own_tasks():
    client.post("/tasks", json={"title": "A", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "B", "priority": 3}, headers={"X-User-Id": "20"})
    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_by_status():
    client.post("/tasks", json={"title": "A", "status": "todo", "priority": 3}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "B", "status": "done", "priority": 3}, headers={"X-User-Id": "10"})
    response = client.get("/tasks?status=done", headers={"X-User-Id": "10"})
    assert len(response.json()) == 1


def test_filter_by_min_priority():
    client.post("/tasks", json={"title": "A", "priority": 2}, headers={"X-User-Id": "10"})
    client.post("/tasks", json={"title": "B", "priority": 4}, headers={"X-User-Id": "10"})
    response = client.get("/tasks?min_priority=3", headers={"X-User-Id": "10"})
    assert len(response.json()) == 1


def test_update_status():
    r = client.post("/tasks", json={"title": "A", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = r.json()["id"]
    response = client.patch(f"/tasks/{task_id}/status", json={"status": "done"}, headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_task_not_found():
    response = client.get("/tasks/999", headers={"X-User-Id": "10"})
    assert response.status_code == 404


def test_delete_task():
    r = client.post("/tasks", json={"title": "A", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = r.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204
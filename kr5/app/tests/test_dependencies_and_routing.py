import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_storage
from app.storage import TaskStorage


@pytest.fixture(autouse=True)
def clean_storage():
    store = TaskStorage()
    app.dependency_overrides[get_storage] = lambda: store
    yield
    store.clear()
    app.dependency_overrides.clear()


client = TestClient(app)


def test_users_me():
    response = client.get("/users/me", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json()["id"] == 10


def test_users_me_no_header():
    response = client.get("/users/me")
    assert response.status_code == 401


def test_admin_stats_forbidden():
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403


def test_admin_stats():
    response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    assert "total_tasks" in response.json()


def test_user_cannot_delete_other_task():
    r = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = r.json()["id"]
    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_admin_can_delete_any_task():
    r = client.post("/tasks", json={"title": "Task", "priority": 3}, headers={"X-User-Id": "10"})
    task_id = r.json()["id"]
    response = client.delete(f"/admin/tasks/{task_id}", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 204
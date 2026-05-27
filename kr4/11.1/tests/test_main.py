import pytest
from fastapi.testclient import TestClient
from app.main import app, db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    db.clear()
    yield
    db.clear()

def test_create_user_valid():
    response = client.post("/users", json={
        "username": "john_doe",
        "age": 25
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "john_doe"
    assert data["age"] == 25
    assert "id" in data

def test_create_user_multiple():
    response1 = client.post("/users", json={
        "username": "alice",
        "age": 30
    })
    response2 = client.post("/users", json={
        "username": "bob",
        "age": 28
    })
    assert response1.status_code == 201
    assert response2.status_code == 201
    assert response1.json()["id"] != response2.json()["id"]

def test_get_user_existing():
    create_response = client.post("/users", json={
        "username": "charlie",
        "age": 35
    })
    user_id = create_response.json()["id"]
    
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert data["username"] == "charlie"

def test_get_user_not_found():
    response = client.get("/users/9999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_delete_user_existing():
    create_response = client.post("/users", json={
        "username": "dave",
        "age": 40
    })
    user_id = create_response.json()["id"]
    
    delete_response = client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

def test_delete_user_not_found():
    response = client.delete("/users/9999")
    assert response.status_code == 404

def test_delete_user_twice():
    create_response = client.post("/users", json={
        "username": "eve",
        "age": 32
    })
    user_id = create_response.json()["id"]
    
    first_delete = client.delete(f"/users/{user_id}")
    assert first_delete.status_code == 204
    
    second_delete = client.delete(f"/users/{user_id}")
    assert second_delete.status_code == 404

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_custom_exception_a_triggered():
    response = client.post("/condition-endpoint", json={"value": -5})
    assert response.status_code == 400
    data = response.json()
    assert data["status_code"] == 400
    assert "positive" in data["detail"].lower()

def test_custom_exception_b_triggered():
    response = client.get("/resource/200")
    assert response.status_code == 404
    data = response.json()
    assert data["status_code"] == 404
    assert "not found" in data["detail"].lower()

def test_condition_endpoint_valid():
    response = client.post("/condition-endpoint", json={"value": 10})
    assert response.status_code == 200
    assert response.json()["value"] == 10

def test_get_resource_valid():
    response = client.get("/resource/50")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 50
    assert "Resource" in data["name"]

def test_validate_user_valid():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "secure_pass123"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_validate_user_invalid_age():
    user_data = {
        "username": "testuser",
        "age": 18,
        "email": "test@example.com",
        "password": "secure_pass123"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 422

def test_validate_user_invalid_email():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "invalid-email",
        "password": "secure_pass123"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 422

def test_validate_user_password_too_short():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "short"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 422

def test_validate_user_password_too_long():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "this_is_a_very_long_password_that_exceeds_limit"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 422

def test_validate_user_invalid_username():
    user_data = {
        "username": "ab",
        "age": 25,
        "email": "test@example.com",
        "password": "secure_pass123"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 422

def test_validate_user_optional_phone_default():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "secure_pass123"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 200

def test_validate_user_optional_phone_provided():
    user_data = {
        "username": "testuser",
        "age": 25,
        "email": "test@example.com",
        "password": "secure_pass123",
        "phone": "+1234567890"
    }
    response = client.post("/validate-user", json=user_data)
    assert response.status_code == 200

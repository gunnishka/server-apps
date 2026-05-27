import pytest
import pytest_asyncio
import httpx
from faker import Faker
from app.main import app, db
from httpx import AsyncClient, ASGITransport

fake = Faker()

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture(autouse=True)
def reset_db():
    db.clear()
    yield
    db.clear()

@pytest.mark.asyncio
async def test_create_user_201(async_client):
    payload = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    response = await async_client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["username"] == payload["username"]
    assert data["age"] == payload["age"]

@pytest.mark.asyncio
async def test_create_user_response_structure(async_client):
    username = fake.user_name()
    age = fake.random_int(min=19, max=80)
    payload = {"username": username, "age": age}
    response = await async_client.post("/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "age" in data
    assert isinstance(data["id"], int)
    assert isinstance(data["username"], str)
    assert isinstance(data["age"], int)

@pytest.mark.asyncio
async def test_get_existing_user_200(async_client):
    create_payload = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    create_response = await async_client.post("/users", json=create_payload)
    user_id = create_response.json()["id"]
    
    get_response = await async_client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert data["username"] == create_payload["username"]
    assert data["age"] == create_payload["age"]

@pytest.mark.asyncio
async def test_get_nonexistent_user_404(async_client):
    response = await async_client.get("/users/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_delete_existing_user_204(async_client):
    create_payload = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    create_response = await async_client.post("/users", json=create_payload)
    user_id = create_response.json()["id"]
    
    delete_response = await async_client.delete(f"/users/{user_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b''

@pytest.mark.asyncio
async def test_delete_nonexistent_user_404(async_client):
    response = await async_client.delete("/users/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_same_user_twice_404(async_client):
    create_payload = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    create_response = await async_client.post("/users", json=create_payload)
    user_id = create_response.json()["id"]
    
    first_delete = await async_client.delete(f"/users/{user_id}")
    assert first_delete.status_code == 204
    
    second_delete = await async_client.delete(f"/users/{user_id}")
    assert second_delete.status_code == 404

@pytest.mark.asyncio
async def test_create_multiple_users(async_client):
    users = []
    for _ in range(3):
        payload = {
            "username": fake.user_name(),
            "age": fake.random_int(min=20, max=60)
        }
        response = await async_client.post("/users", json=payload)
        assert response.status_code == 201
        users.append(response.json())
    
    assert len(users) == 3
    ids = [u["id"] for u in users]
    assert len(set(ids)) == 3

@pytest.mark.asyncio
async def test_isolation_between_tests(async_client):
    payload1 = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    response1 = await async_client.post("/users", json=payload1)
    assert response1.status_code == 201
    user_id = response1.json()["id"]
    
    payload2 = {
        "username": fake.user_name(),
        "age": fake.random_int(min=20, max=60)
    }
    response2 = await async_client.post("/users", json=payload2)
    user2_id = response2.json()["id"]
    
    assert user_id != user2_id

@pytest.mark.asyncio
async def test_get_user_after_create_with_faker_data(async_client):
    username = fake.first_name()
    age = fake.random_int(min=18, max=65)
    payload = {"username": username, "age": age}
    
    create_response = await async_client.post("/users", json=payload)
    assert create_response.status_code == 201
    created_user = create_response.json()
    
    get_response = await async_client.get(f"/users/{created_user['id']}")
    assert get_response.status_code == 200
    retrieved_user = get_response.json()
    assert retrieved_user["username"] == username
    assert retrieved_user["age"] == age

@pytest.mark.asyncio
async def test_edge_case_age_boundary(async_client):
    payload = {
        "username": fake.user_name(),
        "age": 18
    }
    response = await async_client.post("/users", json=payload)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_edge_case_large_age(async_client):
    payload = {
        "username": fake.user_name(),
        "age": 150
    }
    response = await async_client.post("/users", json=payload)
    assert response.status_code == 201

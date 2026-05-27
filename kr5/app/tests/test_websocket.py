import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.room_manager import manager


@pytest.fixture(autouse=True)
def clean_manager():
    manager.rooms.clear()
    yield
    manager.rooms.clear()


client = TestClient(app)


def test_connect_valid_username():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        data = ws.receive_json()
        assert data["type"] == "join"
        assert data["username"] == "alice"


def test_send_message():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "text": "Hello"})
        data = ws.receive_json()
        assert data["type"] == "message"
        assert data["text"] == "Hello"


def test_two_clients_same_room():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
        ws1.receive_json()
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
            join_data = ws1.receive_json()
            assert join_data["username"] == "bob"
            join_data2 = ws2.receive_json()
            assert join_data2["username"] == "bob"


def test_different_rooms():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
        ws1.receive_json()
        with client.websocket_connect("/ws/rooms/java?username=bob") as ws2:
            ws2.receive_json()
            ws1.send_json({"type": "message", "text": "Python only"})
            data = ws1.receive_json()
            assert data["text"] == "Python only"


def test_message_too_long():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()
        long_text = "A" * 301
        ws.send_json({"type": "message", "text": long_text})
        data = ws.receive_json()
        assert data["type"] == "error"


def test_users_list_after_disconnect():
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()
        response = client.get("/rooms/python/users")
        assert "alice" in response.json()["users"]
    response = client.get("/rooms/python/users")
    assert "alice" not in response.json()["users"]
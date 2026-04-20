import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.db import set_db_path, init_db
from app.main import app, _sessions, _chat_history


client = TestClient(app)

_test_db_dir = None


def setup_function():
    global _test_db_dir
    _sessions.clear()
    _chat_history.clear()
    _test_db_dir = tempfile.TemporaryDirectory()
    db_path = Path(_test_db_dir.name) / "test.db"
    set_db_path(db_path)
    init_db()


def teardown_function():
    global _test_db_dir
    if _test_db_dir:
        _test_db_dir.cleanup()
        _test_db_dir = None


def _login() -> str:
    resp = client.post("/api/login", json={"username": "user", "password": "password"})
    return resp.json()["token"]


def test_healthcheck() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_page() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Sign in" in response.text or "Kanban Project" in response.text


# --- Login tests ---


def test_login_success() -> None:
    response = client.post("/api/login", json={"username": "user", "password": "password"})

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert "token" in data
    assert len(data["token"]) > 0


def test_login_wrong_password() -> None:
    response = client.post("/api/login", json={"username": "user", "password": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_username() -> None:
    response = client.post("/api/login", json={"username": "nobody", "password": "password"})

    assert response.status_code == 401


def test_login_missing_fields() -> None:
    response = client.post("/api/login", json={"username": "user"})

    assert response.status_code == 422


# --- /api/me tests ---


def test_me_with_valid_token() -> None:
    token = _login()

    response = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["username"] == "user"


def test_me_without_token() -> None:
    response = client.get("/api/me")

    assert response.status_code == 401


def test_me_with_bad_token() -> None:
    response = client.get("/api/me", headers={"Authorization": "Bearer fake-token"})

    assert response.status_code == 401


# --- Logout tests ---


def test_logout_invalidates_token() -> None:
    token = _login()

    logout = client.post("/api/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200

    me = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 401


def test_logout_without_token() -> None:
    response = client.post("/api/logout")

    assert response.status_code == 200


# --- Board tests ---


def test_get_board_returns_default() -> None:
    token = _login()

    response = client.get("/api/board", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Product Delivery Board"
    assert len(data["columns"]) == 5
    assert data["columns"][0]["title"] == "Intake"
    assert data["columns"][4]["title"] == "Done"


def test_get_board_unauthenticated() -> None:
    response = client.get("/api/board")

    assert response.status_code == 401


def test_update_board_columns() -> None:
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    new_columns = [
        {"id": "col-1", "title": "Todo", "cards": [{"id": "c1", "title": "Task 1", "detail": "Do it"}]},
        {"id": "col-2", "title": "Done", "cards": []},
    ]
    response = client.put("/api/board", headers=headers, json={"columns": new_columns})

    assert response.status_code == 200
    data = response.json()
    assert len(data["columns"]) == 2
    assert data["columns"][0]["title"] == "Todo"
    assert data["columns"][0]["cards"][0]["title"] == "Task 1"


def test_update_board_with_name() -> None:
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    new_columns = [{"id": "col-1", "title": "Backlog", "cards": []}]
    response = client.put(
        "/api/board", headers=headers, json={"columns": new_columns, "name": "My Board"}
    )

    assert response.status_code == 200
    assert response.json()["name"] == "My Board"


def test_update_board_persists() -> None:
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    new_columns = [
        {"id": "col-1", "title": "A", "cards": []},
        {"id": "col-2", "title": "B", "cards": [{"id": "c1", "title": "Card", "detail": ""}]},
    ]
    client.put("/api/board", headers=headers, json={"columns": new_columns})

    response = client.get("/api/board", headers=headers)
    data = response.json()
    assert len(data["columns"]) == 2
    assert data["columns"][1]["cards"][0]["title"] == "Card"


def test_update_board_unauthenticated() -> None:
    response = client.put("/api/board", json={"columns": []})

    assert response.status_code == 401


# --- AI test endpoint ---


def test_ai_test_unauthenticated() -> None:
    response = client.get("/api/ai/test")

    assert response.status_code == 401


@patch("app.main.chat", return_value="4")
def test_ai_test_returns_reply(mock_chat) -> None:
    token = _login()

    response = client.get("/api/ai/test", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["reply"] == "4"
    mock_chat.assert_called_once()


@patch("app.main.chat", side_effect=RuntimeError("OPENROUTER_API_KEY environment variable is not set"))
def test_ai_test_missing_key(mock_chat) -> None:
    token = _login()

    response = client.get("/api/ai/test", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 500


# --- AI chat endpoint tests ---


def _ai_response(reply: str, board_update=None) -> str:
    return json.dumps({"reply": reply, "board_update": board_update})


@patch("app.main.chat_with_board", return_value={"reply": "Hello!", "board_update": None})
def test_ai_chat_reply_only(mock_cwb) -> None:
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/ai/chat", headers=headers, json={"message": "Hi"})

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Hello!"
    assert "board" not in data
    mock_cwb.assert_called_once()


@patch("app.main.chat_with_board")
def test_ai_chat_with_board_update(mock_cwb) -> None:
    new_columns = [
        {"id": "col-1", "title": "Todo", "cards": [{"id": "c1", "title": "New task", "detail": ""}]},
        {"id": "col-2", "title": "Done", "cards": []},
    ]
    mock_cwb.return_value = {"reply": "Created a card.", "board_update": new_columns}
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/ai/chat", headers=headers, json={"message": "Add a task"})

    assert response.status_code == 200
    data = response.json()
    assert data["reply"] == "Created a card."
    assert "board" in data
    assert data["board"]["columns"][0]["cards"][0]["title"] == "New task"

    # Verify board was actually persisted
    board = client.get("/api/board", headers=headers).json()
    assert board["columns"][0]["cards"][0]["title"] == "New task"


@patch("app.main.chat_with_board")
def test_ai_chat_persists_history(mock_cwb) -> None:
    mock_cwb.return_value = {"reply": "First answer", "board_update": None}
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/ai/chat", headers=headers, json={"message": "First question"})

    assert token in _chat_history
    assert len(_chat_history[token]) == 2
    assert _chat_history[token][0] == {"role": "user", "content": "First question"}
    assert _chat_history[token][1] == {"role": "assistant", "content": "First answer"}

    # Second message should include history
    mock_cwb.return_value = {"reply": "Second answer", "board_update": None}
    client.post("/api/ai/chat", headers=headers, json={"message": "Second question"})

    assert len(_chat_history[token]) == 4
    # Verify history was passed to chat_with_board
    call_args = mock_cwb.call_args_list[1]
    history_arg = call_args[0][2]  # third positional arg
    assert len(history_arg) == 2


def test_ai_chat_unauthenticated() -> None:
    response = client.post("/api/ai/chat", json={"message": "Hi"})

    assert response.status_code == 401


@patch("app.main.chat_with_board", side_effect=RuntimeError("OPENROUTER_API_KEY environment variable is not set"))
def test_ai_chat_missing_key(mock_cwb) -> None:
    token = _login()

    response = client.post("/api/ai/chat", headers={"Authorization": f"Bearer {token}"}, json={"message": "Hi"})

    assert response.status_code == 500
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


@patch("app.main.chat_with_board", side_effect=ValueError("AI response is not valid JSON"))
def test_ai_chat_invalid_ai_response(mock_cwb) -> None:
    token = _login()

    response = client.post("/api/ai/chat", headers={"Authorization": f"Bearer {token}"}, json={"message": "Hi"})

    assert response.status_code == 502
    assert "invalid response" in response.json()["detail"]


def test_ai_chat_logout_clears_history() -> None:
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}
    _chat_history[token] = [{"role": "user", "content": "test"}]

    client.post("/api/logout", headers=headers)

    assert token not in _chat_history
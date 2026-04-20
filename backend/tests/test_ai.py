import json
import os
import pytest
from app.ai import (
    get_client,
    chat,
    parse_ai_response,
    build_system_message,
    _validate_columns,
    OPENROUTER_BASE_URL,
    DEFAULT_MODEL,
)


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        get_client()


def test_client_configured(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
    client = get_client()
    assert str(client.base_url).rstrip("/") == OPENROUTER_BASE_URL
    assert client.api_key == "test-key-123"


def test_default_model():
    assert DEFAULT_MODEL == "openai/gpt-oss-120b"


# --- parse_ai_response tests ---


def test_parse_reply_only():
    raw = json.dumps({"reply": "Hello!", "board_update": None})
    result = parse_ai_response(raw)
    assert result["reply"] == "Hello!"
    assert result["board_update"] is None


def test_parse_reply_with_board_update():
    columns = [
        {"id": "col-1", "title": "Todo", "cards": [{"id": "c1", "title": "Task", "detail": ""}]},
        {"id": "col-2", "title": "Done", "cards": []},
    ]
    raw = json.dumps({"reply": "Done!", "board_update": columns})
    result = parse_ai_response(raw)
    assert result["reply"] == "Done!"
    assert len(result["board_update"]) == 2
    assert result["board_update"][0]["cards"][0]["title"] == "Task"


def test_parse_strips_markdown_fences():
    inner = json.dumps({"reply": "Hi", "board_update": None})
    raw = f"```json\n{inner}\n```"
    result = parse_ai_response(raw)
    assert result["reply"] == "Hi"


def test_parse_rejects_non_json():
    with pytest.raises(ValueError, match="not valid JSON"):
        parse_ai_response("This is just text")


def test_parse_rejects_non_object():
    with pytest.raises(ValueError, match="must be a JSON object"):
        parse_ai_response(json.dumps([1, 2, 3]))


def test_parse_rejects_missing_reply():
    with pytest.raises(ValueError, match="missing 'reply'"):
        parse_ai_response(json.dumps({"board_update": None}))


def test_parse_rejects_non_string_reply():
    with pytest.raises(ValueError, match="'reply' must be a string"):
        parse_ai_response(json.dumps({"reply": 123, "board_update": None}))


def test_parse_rejects_non_array_board_update():
    with pytest.raises(ValueError, match="must be an array or null"):
        parse_ai_response(json.dumps({"reply": "hi", "board_update": "bad"}))


def test_parse_rejects_column_missing_id():
    columns = [{"title": "Col"}]
    with pytest.raises(ValueError, match="missing 'id' or 'title'"):
        parse_ai_response(json.dumps({"reply": "hi", "board_update": columns}))


def test_parse_rejects_card_missing_id():
    columns = [{"id": "c1", "title": "Col", "cards": [{"title": "Card"}]}]
    with pytest.raises(ValueError, match="missing 'id' or 'title'"):
        parse_ai_response(json.dumps({"reply": "hi", "board_update": columns}))


def test_parse_rejects_non_object_column():
    with pytest.raises(ValueError, match="must be an object"):
        parse_ai_response(json.dumps({"reply": "hi", "board_update": ["bad"]}))


def test_parse_rejects_non_array_cards():
    columns = [{"id": "c1", "title": "Col", "cards": "bad"}]
    with pytest.raises(ValueError, match="'cards' must be an array"):
        parse_ai_response(json.dumps({"reply": "hi", "board_update": columns}))


# --- build_system_message tests ---


def test_build_system_message_includes_board():
    board = {"columns": [{"id": "c1", "title": "Todo", "cards": []}]}
    msg = build_system_message(board)
    assert msg["role"] == "system"
    assert '"Todo"' in msg["content"]
    assert "c1" in msg["content"]


# --- _validate_columns tests ---


def test_validate_columns_empty():
    _validate_columns([])


def test_validate_columns_valid():
    columns = [
        {"id": "c1", "title": "A", "cards": [{"id": "x", "title": "T", "detail": ""}]},
    ]
    _validate_columns(columns)

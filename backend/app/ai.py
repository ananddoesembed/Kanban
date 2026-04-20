import json
import os
from typing import Any

from openai import OpenAI

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """\
You are a project management assistant. The user has a Kanban board. \
You can answer questions and help manage the board.

Current board state (JSON):
{board_json}

When the user asks you to create, edit, move, or delete cards or rename columns, \
respond with a JSON object containing:
- "reply": a short text message for the user
- "board_update": the full updated columns array (same shape as the board state above)

When the user asks a question that does NOT require changing the board, respond with:
- "reply": your text answer
- "board_update": null

Always respond with valid JSON matching this schema exactly. No markdown fences, no extra keys.\
"""


def get_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set")
    return OpenAI(base_url=OPENROUTER_BASE_URL, api_key=api_key)


def chat(messages: list[dict], model: str | None = None) -> str:
    client = get_client()
    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content


def build_system_message(board: dict) -> dict:
    board_json = json.dumps(board.get("columns", []), indent=2)
    return {"role": "system", "content": SYSTEM_PROMPT.format(board_json=board_json)}


def parse_ai_response(raw: str) -> dict:
    """Parse and validate the AI response JSON.

    Returns a dict with "reply" (str) and "board_update" (list | None).
    Raises ValueError if the response is malformed.
    """
    text = raw.strip()
    # Strip markdown fences if the model wraps its response
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI response is not valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object")

    if "reply" not in data:
        raise ValueError("AI response missing 'reply' field")

    if not isinstance(data["reply"], str):
        raise ValueError("AI response 'reply' must be a string")

    board_update = data.get("board_update")
    if board_update is not None:
        if not isinstance(board_update, list):
            raise ValueError("AI response 'board_update' must be an array or null")
        _validate_columns(board_update)

    return {"reply": data["reply"], "board_update": board_update}


def _validate_columns(columns: list) -> None:
    """Validate that columns match the expected board shape."""
    for i, col in enumerate(columns):
        if not isinstance(col, dict):
            raise ValueError(f"Column {i} must be an object")
        if "id" not in col or "title" not in col:
            raise ValueError(f"Column {i} missing 'id' or 'title'")
        if not isinstance(col.get("cards", []), list):
            raise ValueError(f"Column {i} 'cards' must be an array")
        for j, card in enumerate(col.get("cards", [])):
            if not isinstance(card, dict):
                raise ValueError(f"Column {i} card {j} must be an object")
            if "id" not in card or "title" not in card:
                raise ValueError(f"Column {i} card {j} missing 'id' or 'title'")


def chat_with_board(
    user_message: str,
    board: dict,
    history: list[dict],
) -> dict:
    """Send a chat message with board context and conversation history.

    Returns a dict with "reply" (str) and "board_update" (list | None).
    Raises ValueError if the AI response is malformed.
    Raises RuntimeError if the API key is missing.
    """
    system = build_system_message(board)
    messages = [system] + history + [{"role": "user", "content": user_message}]
    raw = chat(messages)
    return parse_ai_response(raw)

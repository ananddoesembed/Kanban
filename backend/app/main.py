import os
import secrets
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.ai import chat, chat_with_board
from app.db import init_db, verify_user, get_board, update_board


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="Project Management MVP", lifespan=lifespan)


def resolve_frontend_out_dir() -> Path:
  configured_root = os.getenv("PROJECT_ROOT")
  candidates: list[Path] = []

  if configured_root:
    candidates.append(Path(configured_root))

  candidates.append(Path.cwd())
  candidates.extend(Path(__file__).resolve().parents)

  for root in candidates:
    frontend_out = root / "frontend" / "out"
    if frontend_out.exists():
      return frontend_out

  fallback_root = Path(configured_root) if configured_root else Path.cwd()
  return fallback_root / "frontend" / "out"


frontend_out_dir = resolve_frontend_out_dir()

if frontend_out_dir.exists():
  app.mount(
    "/_next",
    StaticFiles(directory=frontend_out_dir / "_next"),
    name="next-static",
  )


# In-memory token store: token -> (username, user_id)
_sessions: dict[str, tuple[str, int]] = {}

# In-memory chat history: token -> list of {"role": ..., "content": ...}
_chat_history: dict[str, list[dict]] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class BoardUpdate(BaseModel):
    columns: list[Any]
    name: str | None = None


class ChatRequest(BaseModel):
    message: str


def _get_token(request: Request) -> str:
    return request.headers.get("authorization", "").removeprefix("Bearer ").strip()


def _get_current_user(request: Request) -> tuple[str, int]:
    token = _get_token(request)
    session = _sessions.get(token)
    if not session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return session


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/login")
def login(body: LoginRequest) -> dict[str, str]:
    user_id = verify_user(body.username, body.password)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_urlsafe(32)
    _sessions[token] = (body.username, user_id)
    return {"token": token, "username": body.username}


@app.post("/api/logout")
def logout(request: Request) -> dict[str, str]:
    token = _get_token(request)
    _sessions.pop(token, None)
    _chat_history.pop(token, None)
    return {"status": "ok"}


@app.get("/api/me")
def me(request: Request) -> dict[str, str]:
    username, _ = _get_current_user(request)
    return {"username": username}


@app.get("/api/board")
def get_board_endpoint(request: Request) -> dict:
    _, user_id = _get_current_user(request)
    board = get_board(user_id)
    if board is None:
        raise HTTPException(status_code=404, detail="No board found")
    return board


@app.put("/api/board")
def update_board_endpoint(request: Request, body: BoardUpdate) -> dict:
    _, user_id = _get_current_user(request)
    result = update_board(user_id, body.columns, body.name)
    if result is None:
        raise HTTPException(status_code=404, detail="No board found")
    return result


@app.get("/api/ai/test")
def ai_test(request: Request) -> dict:
    _get_current_user(request)
    try:
        reply = chat([{"role": "user", "content": "What is 2+2? Reply with just the number."}])
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"reply": reply}


@app.post("/api/ai/chat")
def ai_chat(request: Request, body: ChatRequest) -> dict:
    _, user_id = _get_current_user(request)
    token = _get_token(request)

    board = get_board(user_id)
    if board is None:
        raise HTTPException(status_code=404, detail="No board found")

    history = _chat_history.get(token, [])

    try:
        result = chat_with_board(body.message, board, list(history))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=f"AI returned invalid response: {e}")

    # Apply board update if present
    board_data = None
    if result["board_update"] is not None:
        board_data = update_board(user_id, result["board_update"])

    # Persist conversation turn in memory
    history.append({"role": "user", "content": body.message})
    history.append({"role": "assistant", "content": result["reply"]})
    _chat_history[token] = history

    response: dict = {"reply": result["reply"]}
    if board_data is not None:
        response["board"] = board_data
    return response


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    index_file = frontend_out_dir / "index.html"

    if index_file.exists():
        return index_file.read_text(encoding="utf-8")

    return """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Project Management MVP</title>
    <style>
      :root {
        color-scheme: light;
        --accent-yellow: #ecad0a;
        --blue-primary: #209dd7;
        --purple-secondary: #753991;
        --dark-navy: #032147;
        --gray-text: #888888;
        font-family: "Segoe UI", sans-serif;
      }

      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: linear-gradient(135deg, #f6fbff 0%, #fff7e0 100%);
        color: var(--dark-navy);
      }

      main {
        width: min(680px, calc(100vw - 32px));
        padding: 32px;
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: 0 24px 80px rgba(3, 33, 71, 0.12);
        border-top: 6px solid var(--accent-yellow);
      }

      h1 {
        margin: 0 0 12px;
        font-size: clamp(2rem, 4vw, 3rem);
      }

      p {
        margin: 0 0 16px;
        color: var(--gray-text);
        line-height: 1.5;
      }

      .pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 14px;
        border-radius: 999px;
        background: rgba(32, 157, 215, 0.12);
        color: var(--blue-primary);
        font-weight: 600;
      }

      code {
        padding: 2px 6px;
        border-radius: 6px;
        background: rgba(117, 57, 145, 0.08);
        color: var(--purple-secondary);
      }
    </style>
  </head>
  <body>
    <main>
      <div class=\"pill\">Scaffold running</div>
      <h1>Hello world</h1>
      <p>
        FastAPI is serving this temporary page from <code>/</code>. The page also checks the backend API so the container can be validated end to end.
      </p>
      <p id=\"api-status\">Checking <code>/api/health</code>...</p>
    </main>
    <script>
      async function loadStatus() {
        const target = document.getElementById("api-status");

        try {
          const response = await fetch("/api/health");
          const payload = await response.json();
          target.textContent = `API status: ${payload.status}`;
        } catch (error) {
          target.textContent = "API status: unavailable";
        }
      }

      loadStatus();
    </script>
  </body>
</html>
"""
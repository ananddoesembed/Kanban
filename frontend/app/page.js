"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import LoginScreen from "./LoginScreen";
import ChatSidebar from "./ChatSidebar";

let nextCardId = Date.now();
function genCardId() {
  return "card-" + (nextCardId++);
}

// --- API helpers ---

async function fetchBoard(token) {
  const res = await fetch("/api/board", {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to load board");
  return res.json();
}

async function saveBoard(token, board) {
  const res = await fetch("/api/board", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ columns: board.columns, name: board.name }),
  });
  if (!res.ok) throw new Error("Failed to save board");
  return res.json();
}

// --- Drag state (module-level to avoid re-renders) ---
let dragCardId = null;
let dragSourceColId = null;

// --- Components ---

function Card({ card, columnId, onUpdate, onDelete, onDragStart, onDragOver, onDrop }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(card.title);
  const [detail, setDetail] = useState(card.detail);
  const titleRef = useRef(null);

  useEffect(() => { setTitle(card.title); }, [card.title]);
  useEffect(() => { setDetail(card.detail); }, [card.detail]);

  const save = () => {
    const trimmed = title.trim();
    if (!trimmed) { setTitle(card.title); setEditing(false); return; }
    onUpdate(card.id, { title: trimmed, detail: detail.trim() });
    setEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); save(); }
    if (e.key === "Escape") { setTitle(card.title); setDetail(card.detail); setEditing(false); }
  };

  if (editing) {
    return (
      <article className="card card-editing">
        <input
          ref={titleRef}
          className="card-title-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={handleKeyDown}
          autoFocus
        />
        <textarea
          className="card-detail-input"
          value={detail}
          onChange={(e) => setDetail(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
        />
        <div className="card-edit-actions">
          <button type="button" onClick={save}>Save</button>
          <button type="button" onClick={() => { setTitle(card.title); setDetail(card.detail); setEditing(false); }}>Cancel</button>
        </div>
      </article>
    );
  }

  return (
    <article
      className="card"
      draggable
      onDragStart={(e) => { e.dataTransfer.effectAllowed = "move"; onDragStart(card.id, columnId); }}
      onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; onDragOver(card.id); }}
      onDrop={(e) => { e.preventDefault(); onDrop(columnId, card.id); }}
    >
      <div className="card-actions">
        <button type="button" onClick={() => { setEditing(true); }}>Edit</button>
        <button type="button" onClick={() => onDelete(card.id)}>Delete</button>
      </div>
      <h3>{card.title}</h3>
      <p>{card.detail}</p>
    </article>
  );
}

function Column({ column, onRename, onAddCard, onUpdateCard, onDeleteCard, onDragStart, onDragOver, onDrop }) {
  const [editingName, setEditingName] = useState(false);
  const [name, setName] = useState(column.title);

  useEffect(() => { setName(column.title); }, [column.title]);

  const saveName = () => {
    const trimmed = name.trim();
    if (!trimmed) { setName(column.title); setEditingName(false); return; }
    onRename(column.id, trimmed);
    setEditingName(false);
  };

  return (
    <section
      className="column"
      onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }}
      onDrop={(e) => { e.preventDefault(); onDrop(column.id, null); }}
    >
      <header className="column-header">
        {editingName ? (
          <input
            className="column-name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={saveName}
            onKeyDown={(e) => { if (e.key === "Enter") saveName(); if (e.key === "Escape") { setName(column.title); setEditingName(false); } }}
            autoFocus
          />
        ) : (
          <h2 onDoubleClick={() => setEditingName(true)}>{column.title}</h2>
        )}
        <span>{column.cards.length} items</span>
      </header>
      <div className="card-stack">
        {column.cards.map((card) => (
          <Card
            key={card.id}
            card={card}
            columnId={column.id}
            onUpdate={onUpdateCard}
            onDelete={(cardId) => onDeleteCard(column.id, cardId)}
            onDragStart={onDragStart}
            onDragOver={onDragOver}
            onDrop={onDrop}
          />
        ))}
      </div>
      <button type="button" className="add-card-button" onClick={() => onAddCard(column.id)}>
        Add Card
      </button>
    </section>
  );
}

export default function HomePage() {
  const [token, setToken] = useState(null);
  const [username, setUsername] = useState(null);
  const [board, setBoard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [chatOpen, setChatOpen] = useState(false);
  const saveTimer = useRef(null);

  // Debounced save
  const scheduleSave = useCallback((tok, updated) => {
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      saveBoard(tok, updated).catch(() => {});
    }, 400);
  }, []);

  const updateBoard = useCallback((fn) => {
    setBoard((prev) => {
      const next = fn(prev);
      scheduleSave(token, next);
      return next;
    });
  }, [token, scheduleSave]);

  // Load board after login
  useEffect(() => {
    if (!token) return;
    setLoading(true);
    setError(null);
    fetchBoard(token)
      .then((data) => setBoard(data))
      .catch(() => setError("Failed to load board."))
      .finally(() => setLoading(false));
  }, [token]);

  const handleLogin = useCallback((tok, user) => {
    setToken(tok);
    setUsername(user);
  }, []);

  const handleLogout = useCallback(async () => {
    if (saveTimer.current) clearTimeout(saveTimer.current);
    if (token) {
      await fetch("/api/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});
    }
    setToken(null);
    setUsername(null);
    setBoard(null);
    setChatOpen(false);
  }, [token]);

  const handleBoardUpdate = useCallback((updated) => {
    setBoard(updated);
  }, []);

  // Board mutations
  const handleRenameColumn = useCallback((colId, newTitle) => {
    updateBoard((b) => ({
      ...b,
      columns: b.columns.map((c) => c.id === colId ? { ...c, title: newTitle } : c),
    }));
  }, [updateBoard]);

  const handleAddCard = useCallback((colId) => {
    const id = genCardId();
    updateBoard((b) => ({
      ...b,
      columns: b.columns.map((c) =>
        c.id === colId
          ? { ...c, cards: [...c.cards, { id, title: "New card", detail: "" }] }
          : c
      ),
    }));
  }, [updateBoard]);

  const handleUpdateCard = useCallback((cardId, fields) => {
    updateBoard((b) => ({
      ...b,
      columns: b.columns.map((c) => ({
        ...c,
        cards: c.cards.map((card) => card.id === cardId ? { ...card, ...fields } : card),
      })),
    }));
  }, [updateBoard]);

  const handleDeleteCard = useCallback((colId, cardId) => {
    updateBoard((b) => ({
      ...b,
      columns: b.columns.map((c) =>
        c.id === colId ? { ...c, cards: c.cards.filter((card) => card.id !== cardId) } : c
      ),
    }));
  }, [updateBoard]);

  // Drag and drop
  const handleDragStart = useCallback((cardId, colId) => {
    dragCardId = cardId;
    dragSourceColId = colId;
  }, []);

  const handleDragOver = useCallback(() => {}, []);

  const handleDrop = useCallback((targetColId, targetCardId) => {
    if (!dragCardId || !dragSourceColId) return;
    const srcCardId = dragCardId;
    const srcColId = dragSourceColId;
    dragCardId = null;
    dragSourceColId = null;

    if (srcColId === targetColId && srcCardId === targetCardId) return;

    updateBoard((b) => {
      const srcCol = b.columns.find((c) => c.id === srcColId);
      if (!srcCol) return b;
      const card = srcCol.cards.find((c) => c.id === srcCardId);
      if (!card) return b;

      const newColumns = b.columns.map((col) => {
        let cards = col.cards.filter((c) => c.id !== srcCardId);
        if (col.id === targetColId) {
          if (targetCardId) {
            const idx = cards.findIndex((c) => c.id === targetCardId);
            cards = [...cards.slice(0, idx), card, ...cards.slice(idx)];
          } else {
            cards = [...cards, card];
          }
        }
        return { ...col, cards };
      });
      return { ...b, columns: newColumns };
    });
  }, [updateBoard]);

  if (!token) {
    return <LoginScreen onLogin={handleLogin} />;
  }

  if (loading) {
    return (
      <div className="shell">
        <div className="loading-message">Loading board...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="shell">
        <div className="loading-message error">{error}</div>
      </div>
    );
  }

  if (!board) return null;

  return (
    <div className="shell">
      <aside className="rail">
        <div>
          <p className="eyebrow">Cobalt Kinetic</p>
          <h1>Kanban Project</h1>
        </div>
        <nav>
          <a href="#board" className="active">Board</a>
        </nav>
        <div className="rail-footer">
          <p>Signed in as <strong>{username}</strong></p>
          <button type="button" className="logout-button" onClick={handleLogout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Cobalt Kinetic</p>
            <h2>{board.name}</h2>
          </div>
          <div className="topbar-actions">
            <span className="status-pill">Local MVP</span>
            <button type="button" className="chat-toggle" onClick={() => setChatOpen((v) => !v)}>
              {chatOpen ? "Close Chat" : "AI Chat"}
            </button>
          </div>
        </header>

        <section className="board" id="board" aria-label="Kanban board">
          {board.columns.map((column) => (
            <Column
              key={column.id}
              column={column}
              onRename={handleRenameColumn}
              onAddCard={handleAddCard}
              onUpdateCard={handleUpdateCard}
              onDeleteCard={handleDeleteCard}
              onDragStart={handleDragStart}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            />
          ))}
        </section>
      </main>

      {chatOpen && <ChatSidebar token={token} onBoardUpdate={handleBoardUpdate} />}
    </div>
  );
}
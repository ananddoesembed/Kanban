# Database Schema

SQLite database at `data/pm.db`, auto-created on startup.

## Tables

### users

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | NOT NULL UNIQUE |
| password_hash | TEXT | NOT NULL |
| salt | TEXT | NOT NULL |

### boards

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL REFERENCES users(id) |
| name | TEXT | NOT NULL DEFAULT 'Product Delivery Board' |
| columns_json | TEXT | NOT NULL DEFAULT '[]' |

## Storage approach

Board state is a single JSON blob in `columns_json`. The shape matches the frontend data model:

```json
[
  {
    "id": "col-1",
    "title": "Intake",
    "cards": [
      { "id": "card-1", "title": "Task", "detail": "Description" }
    ]
  }
]
```

One read / one write per board save. No card or column join tables.

## Seeding

On first startup, the MVP user (`user` / `password`) is created with a salted SHA-256 hash and an empty 5-column board.

## Chat history

Deferred. Chat history is kept in-memory per session for the MVP. A `chat_history` table can be added later without schema migration.

## Migrations

None. Tables are created with `CREATE TABLE IF NOT EXISTS` on startup.

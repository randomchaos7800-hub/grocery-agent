"""SQLite database layer for the grocery list."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "grocery.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity TEXT DEFAULT '1',
                category TEXT DEFAULT '',
                checked INTEGER DEFAULT 0,
                added_by TEXT NOT NULL,
                added_at TEXT NOT NULL,
                notes TEXT DEFAULT ''
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_items_checked ON items(checked)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_items_name ON items(name COLLATE NOCASE)")


def add_item(name: str, quantity: str, added_by: str, category: str = "", notes: str = "") -> int:
    """Add an item. Returns new item id."""
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO items (name, quantity, category, added_by, added_at, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (name, quantity, category, added_by, now, notes),
        )
        return cur.lastrowid


def remove_item(item_id: int) -> bool:
    """Delete item by id. Returns True if deleted."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        return cur.rowcount > 0


def set_checked(item_id: int, checked: bool) -> bool:
    """Set checked state. Returns True if updated."""
    with _connect() as conn:
        cur = conn.execute("UPDATE items SET checked = ? WHERE id = ?", (int(checked), item_id))
        return cur.rowcount > 0


def get_all_items() -> list[dict]:
    """Return all items: unchecked first, then checked, sorted by name."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY checked ASC, name COLLATE NOCASE ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def find_by_name(name: str) -> list[dict]:
    """Find items whose name contains the given string (case-insensitive)."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM items WHERE name LIKE ? COLLATE NOCASE",
            (f"%{name}%",),
        ).fetchall()
        return [dict(r) for r in rows]


def get_by_id(item_id: int) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None


def clear_checked() -> int:
    """Delete all checked items. Returns count deleted."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM items WHERE checked = 1")
        return cur.rowcount


def clear_all() -> int:
    """Delete every item. Returns count deleted."""
    with _connect() as conn:
        cur = conn.execute("DELETE FROM items")
        return cur.rowcount

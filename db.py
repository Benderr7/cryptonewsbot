# Хранилище уже отправленных новостей, чтобы не повторять их в сводках
import sqlite3

DB_PATH = "digest.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sent (url TEXT PRIMARY KEY, sent_at TEXT)")


def filter_new(items):
    """Оставляет только новости, которых ещё не было в сводках."""
    with sqlite3.connect(DB_PATH) as conn:
        seen = {row[0] for row in conn.execute("SELECT url FROM sent")}
    return [it for it in items if it["url"] not in seen]


def mark_sent(items):
    """Запоминает новости как отправленные."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.executemany(
            "INSERT OR IGNORE INTO sent (url, sent_at) VALUES (?, datetime('now'))",
            [(it["url"],) for it in items],
        )

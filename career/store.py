import hashlib
import json
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo
from .config import ROOT

def now():
    return datetime.now(ZoneInfo("Europe/London")).isoformat()

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

class Store:
    def __init__(self, path=None):
        self.path = path or ROOT / "private" / "career.sqlite"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=15)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS records (
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL,
          status TEXT NOT NULL, body TEXT NOT NULL, source TEXT NOT NULL,
          updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs (
          id INTEGER PRIMARY KEY, cache_key TEXT NOT NULL, task TEXT NOT NULL,
          day TEXT NOT NULL, status TEXT NOT NULL, output TEXT,
          input_tokens INTEGER, output_tokens INTEGER, cost REAL,
          error TEXT, created TEXT NOT NULL);
        CREATE UNIQUE INDEX IF NOT EXISTS active_cache ON runs(cache_key)
          WHERE status IN ('running', 'done');
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, record_id TEXT, action TEXT, created TEXT);
        ''')

    def put(self, id, kind, title, status, body, source=""):
        if not isinstance(body, str):
            body = json.dumps(body, ensure_ascii=False)
        with self.db:
            self.db.execute('''INSERT INTO records VALUES (?,?,?,?,?,?,?)
              ON CONFLICT(id) DO UPDATE SET title=excluded.title, status=excluded.status,
              body=excluded.body, source=excluded.source, updated=excluded.updated''',
              (id, kind, title, status, body, source, now()))

    def get(self, id):
        row = self.db.execute("SELECT * FROM records WHERE id=?", (id,)).fetchone()
        return dict(row) if row else None

    def records(self, kind=None):
        sql = "SELECT * FROM records"
        rows = self.db.execute(sql + (" WHERE kind=?" if kind else "") + " ORDER BY updated DESC", (kind,) if kind else ())
        return [dict(r) for r in rows]

    def setting(self, key, default=""):
        r = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return r[0] if r else default

    def set_setting(self, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, value))

    def claim_slot(self, key):
        with self.db:
            cursor = self.db.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', (key,'running'))
            return cursor.rowcount == 1

    def reserve(self, key, task, cap):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            cached = self.db.execute("SELECT * FROM runs WHERE cache_key=? AND status='done'", (key,)).fetchone()
            if cached:
                self.db.commit()
                return dict(cached), True
            if self.db.execute("SELECT 1 FROM runs WHERE status='running'").fetchone():
                raise ValueError("A run is in progress or was interrupted. Check it before retrying.")
            if self.setting("api_blocked"):
                raise ValueError("API paused after a quota/authentication failure. Resolve it and reset API status.")
            day = now()[:10]
            count = self.db.execute("SELECT count(*) FROM runs WHERE day=?", (day,)).fetchone()[0]
            if count >= cap:
                raise ValueError("Daily API call limit reached. Cached results remain available.")
            cur = self.db.execute("INSERT INTO runs(cache_key,task,day,status,created) VALUES(?,?,?,'running',?)", (key,task,day,now()))
            self.db.commit()
            return {"id": cur.lastrowid}, False
        except Exception:
            self.db.rollback()
            raise

    def finish(self, id, output, usage, cost=None):
        with self.db:
            self.db.execute("UPDATE runs SET status='done', output=?, input_tokens=?, output_tokens=?, cost=? WHERE id=?", (output, *usage, cost, id))

    def fail(self, id, code):
        with self.db:
            self.db.execute("UPDATE runs SET status='failed', error=? WHERE id=?", (code,id))
        if code in {"insufficient_quota", "authentication"}:
            self.set_setting("api_blocked", code)

    def transition(self, id, target):
        allowed = {
          "draft": {"approved", "rejected"}, "approved": {"completed", "rejected"},
          "saved": {"applied", "rejected"}, "applied": {"responded", "rejected", "interview"},
          "responded": {"interview", "rejected"}, "interview": {"offer", "rejected"},
          "pending": {"accepted", "declined"},
        }
        with self.db:
            row = self.get(id)
            if not row or target not in allowed.get(row["status"], set()):
                raise ValueError("Invalid status change")
            self.db.execute("UPDATE records SET status=?, updated=? WHERE id=?", (target,now(),id))
            self.db.execute("INSERT INTO events(record_id,action,created) VALUES(?,?,?)", (id,target,now()))

    def close(self):
        self.db.close()

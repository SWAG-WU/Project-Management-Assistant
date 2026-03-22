import sqlite3
from datetime import datetime
from config import IDEAS_DB_FILE

def init_db():
    conn = sqlite3.connect(IDEAS_DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        source_url TEXT UNIQUE,
        tags TEXT,
        difficulty TEXT,
        estimated_days INTEGER,
        status TEXT DEFAULT 'unused',
        collected_at TEXT
    )''')
    conn.commit()
    conn.close()

def add_idea(title, description, source_url, tags="", difficulty="medium", estimated_days=7):
    conn = sqlite3.connect(IDEAS_DB_FILE)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO ideas
            (title, description, source_url, tags, difficulty, estimated_days, collected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (title, description, source_url, tags, difficulty, estimated_days, datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def list_ideas(status=None, limit=20):
    conn = sqlite3.connect(IDEAS_DB_FILE)
    c = conn.cursor()
    if status:
        c.execute('SELECT * FROM ideas WHERE status=? ORDER BY collected_at DESC LIMIT ?', (status, limit))
    else:
        c.execute('SELECT * FROM ideas ORDER BY collected_at DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows

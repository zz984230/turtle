import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
import time

class TextStorage:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parents[2] / 'data' / 'text.db'
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _init(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT, url TEXT UNIQUE, title TEXT, published_at TEXT, content TEXT, created_at INTEGER)'
        )
        con.commit()
        con.close()

    def save_documents(self, docs: List[Dict]):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        now = int(time.time())
        for d in docs:
            cur.execute(
                'INSERT OR IGNORE INTO documents (source, url, title, published_at, content, created_at) VALUES (?,?,?,?,?,?)',
                (d.get('source'), d.get('url'), d.get('title'), d.get('published_at'), d.get('content'), now)
            )
        con.commit()
        con.close()

    def query(self, keyword: str, limit: int = 50) -> List[Dict]:
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute('SELECT source, url, title, published_at FROM documents WHERE content LIKE ? ORDER BY id DESC LIMIT ?', (f'%{keyword}%', limit))
        rows = cur.fetchall()
        con.close()
        return [{'source': r[0], 'url': r[1], 'title': r[2], 'published_at': r[3]} for r in rows]
import sqlite3
from typing import List, Tuple, Optional
from os.path import join
class MessageDatabase:
    def __init__(self, db_path: str):
        self.db_path = join(db_path,"messages.db")
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    data BLOB NOT NULL,
                    type INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    dialog_hash TEXT NOT NULL
                )
            ''')
            conn.commit()

    def add_message(self, sender: str, data: bytes, type: int, timestamp: float, dialog_hash: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (sender, data, type, timestamp, dialog_hash)
                VALUES (?, ?, ?, ?, ?)
            ''', (sender, data, type, timestamp, dialog_hash))
            conn.commit()

    def get_messages(self, after_timestamp: float) -> List[Tuple[int, str, bytes, int, float, str]]:
        '''sender, data, type, timestamp, dialog_hash'''
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, data, type, timestamp, dialog_hash
                FROM messages
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (after_timestamp,))
            return [(row['sender'], row['data'], row['type'], row['timestamp'], row['dialog_hash'])
                    for row in cursor.fetchall()]

    def delete_type_five_messages(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE type = 5')
            conn.commit()

    def get_max_timestamp(self) -> Optional[float]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(timestamp) FROM messages')
            result = cursor.fetchone()[0]
            return result
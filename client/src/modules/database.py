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
            # Если type=5, проверяем наличие сообщения с type=5 для данного dialog_hash
            if type == 5:
                cursor.execute('''
                    SELECT id FROM messages
                    WHERE dialog_hash = ? AND type = 5
                ''', (dialog_hash,))
                existing_message = cursor.fetchone()
                if existing_message:
                    # Если сообщение существует, обновляем его
                    cursor.execute('''
                        UPDATE messages
                        SET sender = ?, data = ?, timestamp = ?
                        WHERE id = ?
                    ''', (sender, data, timestamp, existing_message[0]))
                else:
                    # Если сообщения нет, вставляем новое
                    cursor.execute('''
                        INSERT INTO messages (sender, data, type, timestamp, dialog_hash)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (sender, data, type, timestamp, dialog_hash))
            else:
                # Для других типов просто вставляем
                cursor.execute('''
                    INSERT INTO messages (sender, data, type, timestamp, dialog_hash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (sender, data, type, timestamp, dialog_hash))
            conn.commit()

    def get_messages(self,dialog_hash: str, after_timestamp: float) -> List[Tuple[int, str, bytes, int, float, str]]:
        '''sender, data, type, timestamp, dialog_hash'''
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sender, data, type, timestamp
                FROM messages
                WHERE timestamp > ? AND dialog_hash = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (after_timestamp,dialog_hash))
            return [(row['sender'], row['data'], row['type'], row['timestamp'])
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
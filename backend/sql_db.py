import sqlite3
from datetime import datetime
from pathlib import Path

from werkzeug.datastructures import FileStorage

from database import Database


class SQLiteDatabase(Database):
    def __init__(self, db_file: str = "database.sqlite"):
        super().__init__()
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        """Create the database table if it does not exist."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS file_entries (
                    unique_id TEXT PRIMARY KEY,
                    file_path TEXT,
                    file_name TEXT,
                    text TEXT,
                    expiration_time INTEGER,
                    has_file INTEGER,
                    instant_expire INTEGER
                )
            """)

    def entry_present(self, unique_id: str) -> bool:
        query = "SELECT 1 FROM file_entries WHERE unique_id = ?"
        result = self.conn.execute(query, (unique_id,)).fetchone()
        return result is not None

    def file_present(self, unique_id: str) -> bool:
        query = "SELECT has_file FROM file_entries WHERE unique_id = ?"
        result = self.conn.execute(query, (unique_id,)).fetchone()
        return result[0] == 1 if result else False

    def add_to_database(self, unique_id: str, file_name: str, file: FileStorage, text: str, expiration_time: int,
                        instant_expire: bool):
        if self.entry_present(unique_id):
            raise ValueError(f"Entry with unique id '{unique_id}' already exists in the database.")

        file_path = None
        if file:
            file_path = f"./files/{unique_id}"
            Path("./files").mkdir(exist_ok=True)  # Ensure the directory exists
            file.save(file_path)

        with self.conn:
            self.conn.execute("""
                INSERT INTO file_entries (unique_id, file_path, file_name, text, expiration_time, has_file, instant_expire)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (unique_id, file_path, file_name, text, expiration_time, bool(file_name), instant_expire))

    def delete_from_database(self, unique_id: str):
        entry = self._get_entry(unique_id)
        if not entry:
            raise KeyError(f"Entry with id '{unique_id}' not found in the database.")

        file_path = entry["file_path"]
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()

        with self.conn:
            self.conn.execute("DELETE FROM file_entries WHERE unique_id = ?", (unique_id,))

    def retrieve_file_path(self, unique_id: str) -> Path:
        entry = self._get_entry(unique_id)
        if not entry or not entry["has_file"]:
            raise FileNotFoundError()
        return Path(entry["file_path"])

    def retrieve_file_name(self, unique_id: str) -> str:
        entry = self._get_entry(unique_id)
        if not entry or not entry["has_file"]:
            raise FileNotFoundError()
        return entry["file_name"]

    def retrieve_text(self, unique_id: str) -> str:
        entry = self._get_entry(unique_id)
        if not entry:
            raise FileNotFoundError()
        return entry["text"]

    def check_expired(self, unique_id: str) -> bool:
        entry = self._get_entry(unique_id)
        if not entry:
            raise FileNotFoundError()
        expired = datetime.now().timestamp() >= entry["expiration_time"]
        if expired:
            self.delete_from_database(unique_id)
        return expired

    def get_instant_expire(self, unique_id: str) -> bool:
        entry = self._get_entry(unique_id)
        if not entry:
            raise FileNotFoundError()
        return bool(entry["instant_expire"])

    def _get_entry(self, unique_id: str) -> dict:
        query = "SELECT * FROM file_entries WHERE unique_id = ?"
        result = self.conn.execute(query, (unique_id,)).fetchone()
        if not result:
            return None
        return {
            "unique_id": result[0],
            "file_path": result[1],
            "file_name": result[2],
            "text": result[3],
            "expiration_time": result[4],
            "has_file": bool(result[5]),
            "instant_expire": bool(result[6]),
        }

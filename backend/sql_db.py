import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import threading

from werkzeug.datastructures import FileStorage

from database import Database


class SQLiteDatabase(Database):
    def __init__(self, db_file: str = "database.sqlite"):
        super().__init__()
        self.conn = sqlite3.connect(db_file, check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self._create_table()
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._start_cleanup_scheduler()

    def _create_table(self):
        """Create the database tables if they do not exist."""
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS URLMetadata
                (
                    ID TEXT PRIMARY KEY,
                    UploadTime DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Store as UNIX timestamp
                    ExpiryTime DATETIME,
                    InstantExpire BOOLEAN DEFAULT 0,
                    IP TEXT DEFAULT NULL
                );

                CREATE TABLE IF NOT EXISTS Text
                (
                    TextID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Content VARCHAR(500),
                    ID TEXT,
                    FOREIGN KEY (ID) REFERENCES URLMetadata(ID)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS File
                (
                    FileID INTEGER PRIMARY KEY AUTOINCREMENT,
                    FileName VARCHAR(100),
                    Path VARCHAR(100),
                    ExpiryTime DATETIME DEFAULT NULL,
                    ID TEXT,
                    FOREIGN KEY (ID) REFERENCES URLMetadata(ID)
                        ON DELETE SET NULL
                );
            """)

    def entry_present(self, unique_id: str) -> bool:
        """Check if an entry exists in the URLMetadata table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM URLMetadata WHERE ID = ?", (unique_id,))
        return cursor.fetchone() is not None

    def file_present(self, unique_id: str) -> bool:
        """Check if a file exists for a given entry in the File table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM File WHERE ID = ?", (unique_id,))
        return cursor.fetchone() is not None

    def add_to_database(self, unique_id: str, file_name: str, file: FileStorage, text: str, expiration_time: int,
                        instant_expire: bool, ip_address: str = None):
        print(f"unique_id: {unique_id}, expiration_time: {expiration_time}, instant_expire: {instant_expire}")
        """Add data to the database."""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO URLMetadata (ID, ExpiryTime, InstantExpire, IP)
                VALUES (?, ?, ?, ?)
            """, (unique_id,
                  (datetime.fromtimestamp(expiration_time)).strftime("%Y-%m-%d %H:%M:%S") if expiration_time else None,  # Use integer timestamp directly
                  int(bool(instant_expire)),
                  ip_address))
            if text:
                cursor.execute("""
                    INSERT INTO Text (Content, ID)
                    VALUES (?, ?)
                """, (text, unique_id))

            if file:
                file_path = f"./files/{uuid.uuid1()}"
                Path("./files").mkdir(exist_ok=True)  # Ensure the directory exists
                file.save(file_path)
                cursor.execute("""
                    INSERT INTO File (FileName, Path, ID)
                    VALUES (?, ?, ?)
                """, (file_name, file_path, unique_id))

    def delete_from_database(self, unique_id: str):
        """Delete an entry and its associated data."""
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT InstantExpire FROM URLMetadata WHERE ID = ?", (unique_id,))
            result = cursor.fetchone()
            if result and result[0]:  # If InstantExpire is True
                print("updated time to +1 hour")
                cursor.execute("""
                    UPDATE File
                    SET ExpiryTime = DATETIME('now', '+1 hour')
                    WHERE ID = ?
                """, (unique_id,))

            # Set ID field to blank in File table
            cursor.execute("""
                UPDATE File
                SET ID = NULL
                WHERE ID = ?
            """, (unique_id,))

            self.conn.execute("DELETE FROM URLMetadata WHERE ID = ?", (unique_id,))
            print(f"deleted {unique_id}")
    def retrieve_file_path(self, unique_id: str) -> Path:
        """Retrieve the file path for a given entry."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT Path FROM File WHERE ID = ?", (unique_id,))
        result = cursor.fetchone()
        return Path(result[0]) if result else None

    def retrieve_file_name(self, unique_id: str) -> str:
        """Retrieve the file name for a given entry."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT FileName FROM File WHERE ID = ?", (unique_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def retrieve_text(self, unique_id: str) -> str:
        """Retrieve the text content for a given entry."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT Content FROM Text WHERE ID = ?", (unique_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def check_expired(self, unique_id: str) -> bool:
        """Check if an entry is expired."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT ExpiryTime FROM URLMetadata WHERE ID = ?", (unique_id,))
        result = cursor.fetchone()
        if result and result[0]:
            return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S") < datetime.now()
        return False

    def get_instant_expire(self, unique_id: str) -> bool:
        """Check if an entry is set to instant expire."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT InstantExpire FROM URLMetadata WHERE ID = ?", (unique_id,))
        result = cursor.fetchone()
        return result[0] if result else False

    def _start_cleanup_scheduler(self):
        """Start a background task to run cleanup_db every hour."""
        def schedule_task():
            while True:
                self._cleanup_db()
                threading.Event().wait(timeout=3600)  # Wait for 1 hour

        self._cleanup_db()
        cleanup_thread = threading.Thread(target=schedule_task, daemon=True)
        cleanup_thread.start()

    def _cleanup_db(self):
        """Delete all expired entries from URLMetadata and File tables."""
        with self.conn:
            cursor = self.conn.cursor()

            # Delete from URLMetadata where ExpiryTime is in the past
            cursor.execute("""
                DELETE FROM URLMetadata
                WHERE ExpiryTime IS NOT NULL
                AND ExpiryTime < DATETIME('now')
            """)

            # Fetch the paths of files that need to be unlinked
            cursor.execute("""
                SELECT Path
                FROM File
                WHERE ExpiryTime IS NOT NULL
                AND ExpiryTime < DATETIME('now')
            """)
            files_to_delete = cursor.fetchall()

            # Unlink the files
            for file in files_to_delete:
                file_path = file[0]
                if os.path.exists(file_path):
                    os.unlink(file_path)  # Deletes the file from the file system
                print(f"Unlinked {file_path}")

            # Delete the corresponding table entries
            cursor.execute("""
                DELETE FROM File
                WHERE ExpiryTime IS NOT NULL
                AND ExpiryTime < DATETIME('now')
            """)
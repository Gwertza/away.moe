from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from werkzeug.datastructures import FileStorage


class Database(ABC):
    @abstractmethod
    def entry_present(self, unique_id: str):
        raise NotImplementedError

    @abstractmethod
    def file_present(self, unique_id: str):
        raise NotImplementedError

    @abstractmethod
    def add_to_database(self, unique_id: str, file_name: str, file: FileStorage, text: str, expiration_time: int,
                        instant_expire: bool, ip_address: str):
        raise NotImplementedError

    @abstractmethod
    def delete_from_database(self, unique_id: str):
        raise NotImplementedError

    @abstractmethod
    def retrieve_file_path(self, unique_id: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def retrieve_file_name(self, unique_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def retrieve_text(self, unique_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def check_expired(self, unique_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_instant_expire(self, unique_id: str) -> bool:
        raise NotImplementedError



@dataclass
class FileEntry:
    file_path: Path
    file_name: str
    text: str
    expiration_time: int
    has_file: bool = False
    instant_expire: bool = False


class PythonDatabase(Database):

    def __init__(self):
        super().__init__()
        self.db_path = Path("./files")
        self.db_path.mkdir(exist_ok=True)  # Ensure the storage directory exists
        self.db: dict[str, FileEntry] = {}

    def check_expired(self, unique_id: str) -> bool:
        """Checks if entry is expired and deletes it if it is"""
        if not self.entry_present(unique_id):
            raise FileNotFoundError
        expired = datetime.now().timestamp() >= self.db[unique_id].expiration_time
        print(f"{expired=} expiring in {self.db[unique_id].expiration_time - int(datetime.now().timestamp())}")
        if expired:
            self.delete_from_database(unique_id)
        return expired

    def entry_present(self, file_name: str) -> bool:
        """Check if an entry with the given name exists in the database."""
        return file_name in self.db

    def file_present(self, unique_id: str):
        """Check if a file with the given name exists in the database."""
        if not self.entry_present(unique_id):
            return False
        return self.db[unique_id].has_file

    def retrieve_file_path(self, unique_id: str) -> Path:
        if not self.file_present(unique_id):
            raise FileNotFoundError()
        return self.db[unique_id].file_path

    def retrieve_file_name(self, file_id: str) -> str:
        if not self.file_present(file_id):
            raise FileNotFoundError()
        return self.db[file_id].file_name

    def retrieve_text(self, unique_id: str) -> str:
        if not self.entry_present(unique_id):
            raise FileNotFoundError()
        return self.db[unique_id].text

    def get_instant_expire(self, unique_id: str) -> bool:
        if not self.entry_present(unique_id):
            raise FileNotFoundError()
        return self.db[unique_id].instant_expire

    def add_to_database(self, unique_id: str,
                        file_name: str | None,
                        file: FileStorage | None,
                        text: str,
                        expiration_time: int,
                        instant_expire: bool = False,
                        ip_address: str | None = None):
        """Add a file entry to the database."""
        file_entry_path = self.db_path / unique_id

        if self.entry_present(unique_id):
            raise ValueError(f"Entry with unique id '{unique_id}' already exists in the database.")

        # Save file
        if file is not None:
            file.save(file_entry_path)

        # Add to the in-memory database
        self.db[unique_id] = FileEntry(file_path=file_entry_path,
                                       file_name=file_name,
                                       text=text,
                                       has_file=file_name is not None,
                                       expiration_time=expiration_time,
                                       instant_expire=instant_expire)

    def delete_from_database(self, unique_id: str):
        """Remove a file entry from the database."""
        if not self.entry_present(unique_id):
            raise KeyError(f"Entry with id '{unique_id}' not found in the database.")

        if self.file_present(unique_id):
            # Delete the actual file if it exists
            self.db[unique_id].file_path.unlink()
        # Remove from the in-memory database
        del self.db[unique_id]



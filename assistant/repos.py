from collections.abc import Iterable
import pickle
from enum import StrEnum
import shelve
from typing import IO, Protocol, cast
from pathlib import Path


class Repo[T](Protocol):
    def get(self, id: str, default: T | None = None) -> T | None:
        ...

    def set(self, id: str, value: T) -> None:
        ...

    def items(self) -> Iterable[tuple[str, T]]:
        ...

    def clear(self):
        ...


class RepoType(StrEnum):
    PICKLE = "pickle"
    SHELVE = "shelve"


class ShelveRepo[T]:
    db: shelve.Shelf

    def __init__(self, db_dir: Path, db_name: str):
        self.db_dir = db_dir
        self.db_name = db_name

    def __enter__(self):
        self.db = shelve.open(str(self.db_dir / self.db_name))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def get(self, id: str, default: T | None = None) -> T | None:
        ret = self.db.get(id, default)
        if ret is None:
            return None
        return cast(T, ret)

    def set(self, id: str, value: T) -> None:
        self.db[id] = value

    def items(self):
        return self.db.items()

    def clear(self):
        self.db.clear()


class PickleRepo[T]:
    data: dict[str, T]

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.data = {}


    def __enter__(self):
        try:
            with self.filepath.open("rb") as src:
                self.data = pickle.load(src)
        except FileNotFoundError:
            self.data = {}
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.filepath.open("wb") as dst:
            pickle.dump(self.data, dst)

    def get(self, id: str, default: T | None = None) -> T | None:
        return self.data.get(id, default)

    def set(self, id: str, value: T) -> None:
        self.data[id] = value

    def items(self):
        return self.data.items()

    def clear(self):
        self.data.clear()

import logging
import sqlite3
from abc import ABC, abstractmethod
from typing import List

from fuzzywuzzy import fuzz, process

from .meme import Meme
from .exceptions import Unauthorized


logger = logging.getLogger(__name__)


class MemeStorage(ABC):

    @abstractmethod
    def add(self, new_meme: Meme):
        pass

    @abstractmethod
    def delete_by_file_id(self, file_id, from_user_id):
        """Delete a meme by file_id or a Meme object"""
        pass

    @abstractmethod
    def rename(self, meme_id, new_name, from_user_id):
        pass

    @abstractmethod
    def get(self, meme_id) -> Meme:
        """Get a meme by it's id"""
        pass

    @abstractmethod
    def get_by_file_id(self, file_id) -> Meme:
        """Get a meme by it's file_id"""
        pass

    @abstractmethod
    def get_most_popular(self, max_count) -> List[Meme]:
        pass

    @abstractmethod
    def get_all(self) -> List[Meme]:
        """Returns all memes"""
        pass

    @abstractmethod
    def inc_times_used(self, meme_id):
        pass

    @abstractmethod
    def has_meme_with_file_id(self, file_id) -> bool:
        pass

    def find(self, search_query: str) -> List[Meme]:
        scored_matches = process.extractBests(
            search_query, self.get_all(),
            key=lambda meme: meme.name,
            scorer=fuzz.UWRatio,
            limit=None,
            score_cutoff=55
        )

        if scored_matches:
            matches, _ = zip(*scored_matches)
            return matches
        else:
            return []


class SqliteMemeStorage(MemeStorage):

    def __init__(self, filename):
        self.connection = sqlite3.connect(filename, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        self.connection.execute(
            'CREATE TABLE IF NOT EXISTS memes ('
            ' id         INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,'
            ' file_id    TEXT NOT NULL UNIQUE,'
            ' name	     TEXT NOT NULL,'
            ' owner_id   INTEGER NOT NULL,'
            ' times_used INTEGER NOT NULL DEFAULT 0'
            ')'
        )

    def add(self, new_meme: Meme):

        with self.connection:
            self.connection.execute(
                'INSERT INTO memes (file_id, name, owner_id, times_used)'
                ' VALUES (:file_id, :name, :owner_id, :times_used)',
                new_meme._asdict())

    def delete_by_file_id(self, file_id, from_user_id):
        if from_user_id != self.get_by_file_id(file_id).owner_id:
            raise Unauthorized

        with self.connection:
            self.connection.execute(
                'DELETE FROM memes '
                ' WHERE file_id = ?',
                (file_id,)
            )

    def rename(self, meme_id, new_name, from_user_id):
        if from_user_id != self.get(meme_id).owner_id:
            raise Unauthorized

        with self.connection:
            self.connection.execute(
                'UPDATE memes'
                ' SET name = :new_name'
                ' WHERE id = :id',
                {'new_name': new_name, 'id': meme_id}
            )

    def get(self, meme_id) -> Meme:
        row = self.connection.execute(
            'SELECT * FROM memes'
            ' WHERE id = ?',
            (meme_id,)
        ).fetchone()
        return Meme(**row)

    def get_by_file_id(self, file_id) -> Meme:
        row = self.connection.execute(
            'SELECT * FROM memes'
            ' WHERE file_id = ?',
            (file_id, )
        ).fetchone()
        return Meme(**row)

    def get_most_popular(self, max_count) -> List[Meme]:
        rows = self.connection.execute(
            'SELECT * FROM memes'
            ' ORDER BY times_used DESC'
            ' LIMIT ?',
            (max_count,)
        ).fetchall()
        return [Meme(**r) for r in rows]

    def get_all(self) -> List[Meme]:
        rows = self.connection.execute('SELECT * FROM memes').fetchall()
        return [Meme(**r) for r in rows]

    def inc_times_used(self, meme_id):
        with self.connection:
            self.connection.execute(
                'UPDATE memes'
                ' SET times_used = times_used + 1'
                ' WHERE id = ?',
                (meme_id,)
            )

    def has_meme_with_file_id(self, file_id) -> bool:
        row = self.connection.execute(
            'SELECT EXISTS('
            ' SELECT 1 FROM memes'
            ' WHERE file_id = ?'
            ')',
            (file_id,)
        ).fetchone()
        exists = list(row)[0]  # returns 1 or 0
        return bool(exists)

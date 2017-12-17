import sqlite3


class InlineResultsRingBuffer(object):

    def __init__(self, limit):
        self.connection = sqlite3.connect(':memory:', check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            """
            CREATE TABLE inline_results (
                id TEXT PRIMARY KEY,
                meme_id INTEGER
            );

            -- Number 10 on where statement defines the ring buffer's size
            CREATE TRIGGER delete_tail AFTER INSERT ON inline_results
            BEGIN
                DELETE FROM inline_results
                  WHERE id % 10 = NEW.id % 10
                    AND id != NEW.id;
            END;
            """
        )

    def add(self, id_, meme_id):
        with self.connection:
            self.connection.execute(
                'INSERT INTO inline_results (id, meme_id)'
                ' VALUES (?, ?)',
                (id_, meme_id)
            )

    def get(self, id_):
        row = self.connection.execute(
            'SELECT meme_id FROM inline_results'
            ' WHERE id = ?',
            (id_,)
        ).fetchone()

        if row is None:
            raise KeyError

        return row['meme_id']

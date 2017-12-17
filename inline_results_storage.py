import sqlite3


class InlineResultsRingBuffer(object):

    def __init__(self, limit):
        self.connection = sqlite3.connect(':memory:', check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        if limit > 10000:
            raise ValueError

        self.connection.execute(
            'CREATE TABLE inline_results ('
            '  id INTEGER PRIMARY KEY AUTOINCREMENT,'
            '  result_id TEXT,'
            '  file_id INTEGER,'
            '  from_user_id INTEGER'
            ')'
        )

        self.connection.execute(
            'CREATE UNIQUE INDEX current_user_query'
            '  ON inline_results (file_id, from_user_id)'
        )

        self.connection.execute(
            'CREATE TRIGGER delete_tail AFTER INSERT ON inline_results'
            '  BEGIN'
            '    DELETE FROM inline_results'
            '      WHERE id % {limit:d} = NEW.id % {limit:d}'
            '        AND id != NEW.id;'
            '  END'
            .format(limit=limit)
        )

    def add(self, result_id, file_id, from_user_id):
        with self.connection:
            self.connection.execute(
                'INSERT OR REPLACE INTO inline_results (result_id, file_id, from_user_id)'
                ' VALUES (?, ?, ?)',
                (result_id, file_id, from_user_id)
            )

    def get(self, result_id):
        row = self.connection.execute(
            'SELECT file_id FROM inline_results'
            ' WHERE result_id = ?',
            (result_id,)
        ).fetchone()

        if row is None:
            raise KeyError

        return row['file_id']

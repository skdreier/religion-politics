# documents.store

import common.disable_warnings

import logging
import sqlite3


DB_WRITE_INTERVAL = 2500


class TextStore:
    def __init__(self, conn):
        self.conn = conn
        self._cur = conn.cursor()
        self._ensure_table()
        self._writeq = []

    def get_sent_info(self, coords):  # list of (idx, offset) pairs
        for idx, offset in coords:
            self._cur.execute(_DotgovOps.get_entry, (idx.item(), ))
            row = self._cur.fetchone()

            yield {
                'url': row[0],
                'checksum': row[1],
                'date': str(row[2]),
                'sentence': row[3].split('\n')[offset]
            }

    def reconcile(self):
        self._flush_queue()

    def write(self, sents, vec_idx, meta):
        entry = {
            'doc_id': self.write_idx,
            'url': meta[0],
            'checksum': meta[1],
            'date': meta[2],
            'doc': '\n'.join(sents),
            'vec_start': vec_idx,
            'vec_end': vec_idx + len(sents)
        }

        self._writeq.append(entry)
        self.write_idx += 1

        if self.write_idx % DB_WRITE_INTERVAL == 0:
            self._flush_queue()

    def _ensure_table(self):
        self._cur.execute(_DotgovOps.table_exists)

        if self._cur.fetchone():
            self._cur.execute(_DotgovOps.get_table_size)
            row = self._cur.fetchone()
            if row:
                self.write_idx = row[0] + 1
            else:
                self.write_idx = 0
        else:
            self._cur.execute(_DotgovOps.create_table)
            self.write_idx = 0

    def _flush_queue(self):
        if len(self._writeq) > 0:
            self._cur.executemany(_DotgovOps.insert_entry, self._writeq)
            self.conn.commit()
            self._writeq = []


class _DotgovOps:
    table_exists = '''SELECT name
                        FROM sqlite_master
                        WHERE type = 'table' AND name = 'dotgov' '''

    create_table = '''CREATE TABLE dotgov (
                        id integer PRIMARY KEY,
                        url text NOT NULL,
                        checksum text NOT NULL,
                        date int NOT NULL,
                        doc text NOT NULL,
                        vec_start int NOT NULL,
                        vec_end int NOT NULL)'''

    get_table_size = '''SELECT max(id) FROM dotgov'''

    insert_entry = '''INSERT INTO dotgov VALUES (
                        :doc_id, :url, :checksum, :date,
                        :doc, :vec_start, :vec_end)'''

    get_entry = '''SELECT url, checksum, date, doc
                     FROM dotgov
                     WHERE id = ?'''


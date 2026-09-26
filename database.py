"""
    Table: entries
    Columns:
        id INTEGER PRIMARY KEY
        title TEXT NOT NULL
        username TEXT
        password TEXT NOT NULL
        url TEXT
        notes TEXT
"""

import sqlite3

def open_db(decrypted_bytes):
    connection = sqlite3.connect(":memory:")
    connection.deserialize(decrypted_bytes)
    return connection

def get_password(title, connection):
    cursor = connection.cursor()
    title_attempts = [title, title.upper(), title.lower(), title.capitalize()]

    for t in title_attempts:
        res = cursor.execute(f"SELECT * FROM entries WHERE title = '{t}';")
        rows = res.fetchone()
        if rows is None:
            continue
        elif rows is not None and t is not title:
            used = t
            return rows, used
        else:
            return rows, False # if the original title was used, no need to notificate 

    return None, False # no entry with provided title

def add_password(entry, connection):
    cursor = connection.cursor()
    title = entry["title"]
    username = entry["username"] or None
    password = entry["password"]
    url = entry["url"] or None
    notes = entry["notes"] or None

    cursor.execute("INSERT INTO entries(title, username, password, url, notes) VALUES (?, ?, ?, ?, ?);", [title, username, password, url, notes])
    connection.commit()
    return get_password(title, connection)

def create_db():
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    cursor.execute("""
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    username TEXT,
    password TEXT NOT NULL,
    url TEXT,
    notes TEXT
);""")
    connection.commit()
    return connection


def serialize(connection):
    connection.commit()
    return connection.serialize()
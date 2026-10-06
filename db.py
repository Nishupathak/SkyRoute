import os
import sqlite3
from contextlib import closing

from data import AIRPORTS, FLIGHTS
from graph import Graph

DB_FILE = os.path.join(os.path.dirname(__file__), "skyroute.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS airports (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT NOT NULL REFERENCES airports(code),
    destination TEXT NOT NULL REFERENCES airports(code),
    price INTEGER NOT NULL CHECK (price > 0),
    minutes INTEGER NOT NULL CHECK (minutes > 0)
);
CREATE INDEX IF NOT EXISTS idx_flights_origin ON flights(origin);
CREATE TABLE IF NOT EXISTS searches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    mode TEXT NOT NULL,
    found INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with closing(get_connection()) as conn:
        with conn:
            conn.executescript(SCHEMA)
            count = conn.execute("SELECT COUNT(*) FROM airports").fetchone()[0]
            if count == 0:
                conn.executemany(
                    "INSERT INTO airports (code, name) VALUES (?, ?)",
                    AIRPORTS.items(),
                )
                conn.executemany(
                    "INSERT INTO flights (origin, destination, price, minutes) "
                    "VALUES (?, ?, ?, ?)",
                    FLIGHTS,
                )


def load_graph():
    g = Graph()
    with closing(get_connection()) as conn:
        for row in conn.execute("SELECT code, name FROM airports ORDER BY code"):
            g.add_airport(row["code"], row["name"])
        for row in conn.execute(
            "SELECT origin, destination, price, minutes FROM flights ORDER BY id"
        ):
            g.add_flight(row["origin"], row["destination"],
                         row["price"], row["minutes"])
    return g


def log_search(origin, destination, mode, found):
    with closing(get_connection()) as conn:
        with conn:
            conn.execute(
                "INSERT INTO searches (origin, destination, mode, found) "
                "VALUES (?, ?, ?, ?)",
                (origin, destination, mode, 1 if found else 0),
            )


def recent_searches(limit=5):
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT origin, destination, mode, found, created_at "
            "FROM searches ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in rows]
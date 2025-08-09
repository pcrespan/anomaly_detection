import os
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "training_data")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password")

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=100,
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)


def get_db_connection():
    if connection_pool:
        return connection_pool.getconn()
    else:
        raise Exception("Connection pool not initialized")


def release_db_connection(conn):
    if connection_pool:
        connection_pool.putconn(conn)


def save_training_data(series_id: str, version: str, data: list[dict]):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        records = [
            (series_id, version, point["timestamp"], point["value"])
            for point in data
        ]
        cur.executemany(
            """
            INSERT INTO training_data (series_id, version, timestamp, value)
            VALUES (%s, %s, %s, %s)
            """,
            records
        )
        conn.commit()
        cur.close()
    finally:
        release_db_connection(conn)

def fetch_training_data(series_id: str, version: str) -> list[tuple]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, value
            FROM training_data
            WHERE series_id = %s AND version = %s
            ORDER BY timestamp
        """, (series_id, version))
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        release_db_connection(conn)

import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def _env(*names, default=None):
    for name in names:
        value = os.getenv(name)
        if value not in (None, ""):
            return value
    return default


def get_connection():
    # Supports both the app's local variable names and Railway's native
    # MySQL variables (MYSQLHOST, MYSQLPORT, MYSQLUSER, MYSQLPASSWORD, MYSQLDATABASE).
    return mysql.connector.connect(
        host=_env("MYSQL_HOST", "MYSQLHOST", default="localhost"),
        port=int(_env("MYSQL_PORT", "MYSQLPORT", default="3306")),
        user=_env("MYSQL_USER", "MYSQLUSER", default="root"),
        password=_env("MYSQL_PASSWORD", "MYSQLPASSWORD", default=""),
        database=_env("MYSQL_DATABASE", "MYSQLDATABASE", default="travelpay"),
    )


def fetch_one(query, params=()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()


def fetch_all(query, params=()):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def execute(query, params=()):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()

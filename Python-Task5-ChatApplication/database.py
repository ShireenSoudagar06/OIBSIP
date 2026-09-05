import sqlite3
import hashlib
import os
import binascii
import datetime

DB_PATH = "chat_app.db"


def _hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    salt_hex = binascii.hexlify(salt).decode("ascii")
    hash_hex = binascii.hexlify(hash_bytes).decode("ascii")
    return f"{salt_hex}${hash_hex}"


def _verify_password(stored_password, provided_password):
    salt_hex, hash_hex = stored_password.split("$")
    salt = binascii.unhexlify(salt_hex.encode("ascii"))
    hash_bytes = hashlib.pbkdf2_hmac("sha256", provided_password.encode("utf-8"), salt, 100000)
    return binascii.hexlify(hash_bytes).decode("ascii") == hash_hex


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT NOT NULL,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def register_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."

    if "|" in username or "|" in password:
        return False, "Username and password cannot contain '|'."

    password_hash = _hash_password(password)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        conn.close()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."


def authenticate_user(username, password):
    if not username or not password:
        return False, "Username and password cannot be empty."

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False, "Invalid username or password."

    if _verify_password(row[0], password):
        return True, "Login successful."
    else:
        return False, "Invalid username or password."


def save_message(room, username, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (room, username, message, timestamp) VALUES (?, ?, ?, ?)",
        (room, username, message, timestamp),
    )
    conn.commit()
    conn.close()


def get_message_history(room, limit=50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, message, timestamp FROM messages WHERE room = ? ORDER BY id DESC LIMIT ?",
        (room, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    rows.reverse()
    return rows

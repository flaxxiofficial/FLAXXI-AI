import os
import sqlite3
import hashlib
import secrets
import time
import jwt

DATABASE = os.getenv("DATABASE_PATH","flaxxi.db")

SECRET = os.getenv("SECRET_KEY")

if not SECRET:
    raise RuntimeError("SECRET_KEY is required")


def connect():

    db = sqlite3.connect(DATABASE,timeout=30)

    db.execute("PRAGMA journal_mode=WAL")

    return db


def initialize():

    with connect() as db:

        db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)


def hash_password(password):

    salt = secrets.token_bytes(16)

    hashed = hashlib.scrypt(
        password.encode(),
        salt=salt,
        n=16384,
        r=8,
        p=1
    )

    return salt.hex()+":"+hashed.hex()


def verify_password(password,stored):

    salt,original = stored.split(":")

    hashed = hashlib.scrypt(
        password.encode(),
        salt=bytes.fromhex(salt),
        n=16384,
        r=8,
        p=1
    )

    return secrets.compare_digest(
        hashed.hex(),original
    )


def register(email,password):

    if len(password)<10:
        return False

    try:

        with connect() as db:

            db.execute(
                "INSERT INTO users(email,password) VALUES (?,?)",
                (email.lower(),hash_password(password))
            )

        return True

    except sqlite3.IntegrityError:

        return False


def login(email,password):

    with connect() as db:

        row = db.execute(
            "SELECT id,password FROM users WHERE email=?",
            (email.lower(),)
        ).fetchone()

    if not row or not verify_password(password,row[1]):
        return None

    return jwt.encode(
        {
            "user_id":row[0],
            "exp":int(time.time())+86400
        },
        SECRET,
        algorithm="HS256"
    )


def get_user(token):

    try:

        data = jwt.decode(
            token,
            SECRET,
            algorithms=["HS256"]
        )

        return data["user_id"]

    except jwt.InvalidTokenError:

        return None

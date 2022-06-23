"""
Contains functions to set up and teardown a test database.

Functions:
    setup_db()
        Connects to a sqlite3 database and stores various habits, tasks, and users in it.
    teardown_db()
        Deletes the test database file.

Var:
    db_name: str
        Name of the test database
"""
import uuid
import hashlib
import os
from datetime import datetime, timedelta
from db import get_db

db_name = "test.db"


def setup_db():
    """
    Connects to a sqlite3 database and stores various habits, tasks, and users in it.

    Return:
        db: sqlite3 db
    """
    db = get_db(db_name)
    for user in ["John", "Jane"]:
        __store_user(db, user, user)

    __store_admin(db)

    __store_habit(
        db=db,
        habit_name="sleep eight hours",
        user_name="John",
        created=datetime.now().replace(microsecond=0) - timedelta(days=28),
        period=1,
        deadline=datetime.now().replace(microsecond=0) + timedelta(days=1),
        is_active=True,
        longest=12
    )
    days_since_completed = reversed(list(range(8)))
    for value in days_since_completed:
        __store_task(db, value, "sleep eight hours")

    __store_habit(
        db=db,
        habit_name="go running",
        user_name="John",
        created=datetime.now().replace(microsecond=0) - timedelta(days=17),
        period=3,
        deadline=datetime.now().replace(microsecond=0) + timedelta(days=2),
        is_active=True,
        longest=5
    )
    days_since_completed = [8, 7, 4, 2]
    for value in days_since_completed:
        __store_task(db, value, "go running")

    __store_habit(
        db=db,
        habit_name="see the dentist",
        user_name="John",
        created=datetime.now().replace(microsecond=0) - timedelta(days=400),
        period=180,
        deadline=datetime.now().replace(microsecond=0) + timedelta(days=50),
        is_active=True,
        longest=2
    )
    days_since_completed = [280, 130]
    for value in days_since_completed:
        __store_task(db, value, "see the dentist")

    return db


def teardown_db():
    """Deletes the test database file."""
    os.remove(db_name)


def __store_user(db, user_name, password):
    # Stores a user item in the given database.
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)",
        {
            "user_id": str(uuid.uuid4()),
            "user_name": user_name,
            "password": hashlib.sha3_256(password.encode()).hexdigest(),
            "is_admin": "False"
        }
    )
    db.commit()


def __store_admin(db):
    # Stores an admin item in the given database.
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)",
        {
            "user_id": str(uuid.uuid4()),
            "user_name": "Admin",
            "password": hashlib.sha3_256("Admin".encode()).hexdigest(),
            "is_admin": "True"
        }
    )
    db.commit()


def __store_habit(db, habit_name, user_name, created, period, deadline, is_active, longest):
    # Stores a habit item in the given database.
    cur = db.cursor()
    cur.execute(
        "INSERT INTO habits VALUES (:habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)",
        {
            "habit_id": str(uuid.uuid4()),
            "name": habit_name,
            "user_name": user_name,
            "created": created,
            "period": period,
            "deadline": deadline,
            "is_active": is_active,
            "longest": longest
        }
    )
    db.commit()


def __store_task(db, days_since_completed, habit_name):
    # Stores a task item in the given database.
    created = datetime.now().replace(microsecond=0) - timedelta(days=days_since_completed)
    cur = db.cursor()
    cur.execute(
        "INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
        {
            "task_id": str(uuid.uuid4()),
            "created": created,
            "habit_name": habit_name
        }
    )
    db.commit()

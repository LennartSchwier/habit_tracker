import uuid
from datetime import datetime, timedelta
from db import get_db


def setup_db():
    db = get_db("test.db")
    for user in ["John", "Jane"]:
        __store_user(db, user, user)
    __store_habit(
        db=db,
        habit_name="go running",
        user_name="John",
        created=datetime.now().replace(microsecond=0) - timedelta(days=20),
        period=3,
        deadline=datetime.now().replace(microsecond=0) - timedelta(days=2),
        is_active=True,
        longest=5
    )
    days_since_completed = [8, 7, 4, 2]
    for value in days_since_completed:
        __store_task(db, value, "go running")


def __store_user(db, user_name, password):
    cur = db.cursor()
    cur.execute(
        "INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)",
        {
            "user_id": str(uuid.uuid4()),
            "user_name": user_name,
            "password": password,
            "is_admin": False
        }
    )


def __store_habit(db, habit_name, user_name, created, period, deadline, is_active, longest):
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


def __store_task(db, days_since_completed, habit_id):
    created = datetime.now().replace(microsecond=0) - timedelta(days=days_since_completed)
    cur = db.cursor()
    cur.execute(
        "INSERT INTO tasks VALUES (:task_id, :created, :habit_id)",
        {
            "task_id": str(uuid.uuid4()),
            "created": created,
            "habit_id": habit_id
        }
    )

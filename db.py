import datetime
import sqlite3
import uuid
from custom_exceptions import UserNameAlreadyExistsError, UserNameIsUnknownError, \
    HabitNameIsUnknownError, HabitNameAlreadyExistsError


def get_db(name="main.db"):
    db = sqlite3.connect(name)
    __create_tables(db)
    return db


def store_user_item(db, user_name, password, is_admin):
    if not __is_user_item_stored(db, user_name):
        cur = db.cursor()
        cur.execute("INSERT INTO users VALUES (:user_id, :user_name, :password, :is_admin)",
                    {
                        "user_id": str(uuid.uuid4()),
                        "user_name": user_name,
                        "password": password,
                        "is_admin": is_admin
                    })
        db.commit()
    else:
        raise UserNameAlreadyExistsError


def delete_user_item(db, user_name):
    if __is_user_item_stored(db, user_name):
        cur = db.cursor()
        cur.execute("DELETE FROM users WHERE user_name=:user_name", {"user_name": user_name})
        db.commit()
    else:
        raise UserNameIsUnknownError


def get_user_item_by_name(db, user_name):
    if __is_user_item_stored(db, user_name):
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE user_name=:user_name", {"user_name": user_name})
        return cur.fetchall()
    else:
        return None


def get_all_user_items(db):
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()


def store_habit_item(db, habit_id, name, user_name, created, period, deadline, is_active=True, longest=0):
    if not __is_habit_item_stored(db, name, user_name):
        cur = db.cursor()
        cur.execute("""INSERT INTO habits VALUES (
            :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": habit_id,
                        "name": name,
                        "user_name": user_name,
                        "created": created,
                        "period": period,
                        "deadline": deadline,
                        "is_active": is_active,
                        "longest": longest
                    })
        db.commit()
    else:
        raise HabitNameAlreadyExistsError


def delete_habit_item(db, name, user_name):
    if __is_habit_item_stored(db, name, user_name):
        cur = db.cursor()
        cur.execute("DELETE FROM habits WHERE name=:name AND user_name=:user_name",
                    {
                        "name": name,
                        "user_name": user_name
                    })
        db.commit()
    else:
        raise HabitNameIsUnknownError


def update_streaks_habit_item(db, name, user_name, deadline, longest):
    cur = db.cursor()
    cur.execute("UPDATE habits SET deadline=:deadline, longest=:longest WHERE name=:name AND user_name=:user_name",
                {
                    "name": name,
                    "user_name": user_name,
                    "deadline": deadline,
                    "longest": longest
                })
    db.commit()


def update_active_status_habit_item(db, name, user_name, deadline, is_active):
    cur = db.cursor()
    cur.execute("UPDATE habits SET deadline=:deadline, is_active=:is_active WHERE name=:name AND user_name=:user_name",
                {
                    "name": name,
                    "user_name": user_name,
                    "deadline": deadline,
                    "is_active": is_active
                })
    db.commit()


def get_all_habit_items(db, user_name, is_active):
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE user_name=:user_name AND is_active=:is_active",
                {
                    "user_name": user_name,
                    "is_active": is_active
                })
    return cur.fetchall()


def get_habit_item_by_name(db, name, user_name):
    if __is_habit_item_stored(db, name, user_name):
        cur = db.cursor()
        cur.execute("SELECT * FROM habits WHERE name=:name AND user_name=:user_name",
                    {
                        "name": name,
                        "user_name": user_name
                    })
        return cur.fetchall()
    else:
        return None


def store_task_item(db, created, habit_name):
    cur = db.cursor()
    cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
                {
                    "task_id": str(uuid.uuid4()),
                    "created": created,
                    "habit_name": habit_name
                })
    db.commit()


def get_tasks_by_habit_name(db, habit_name):
    cur = db.cursor()
    cur.execute("SELECT * FROM tasks WHERE habit_name=:habit_name", {"habit_name": habit_name})
    return cur.fetchall()


def remove_tasks_by_habit_name(db, habit_name):
    cur = db.cursor()
    cur.execute("DELETE FROM tasks WHERE habit_name=:habit_name", {"habit_name": habit_name})
    db.commit()


def __create_tables(db):
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS habits (
        habit_id TEXT PRIMARY KEY,
        name TEXT,
        user_name TEXT,
        created DATETIME,
        period INT,
        deadline DATETIME,
        is_active BOOL,
        longest INT
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        user_name TEXT,
        password TEXT,
        is_admin BOOL,
        FOREIGN KEY (user_name) REFERENCES habits(user_name)
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT,
        created DATETIME,
        habit_name TEXT,
        FOREIGN KEY (habit_name) REFERENCES habits(name)
    )""")
    db.commit()


def __is_user_item_stored(db, user_name):
    """Helper function that checks if the habit name is present in the database"""
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE user_name=:user_name", {"user_name": user_name})
    return len(cur.fetchall()) != 0


def __is_habit_item_stored(db, name, user_name):
    """Helper function that checks if the habit name is present in the database"""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE name=:name AND user_name=:user_name",
                {
                    "name": name,
                    "user_name": user_name
                })
    return len(cur.fetchall()) != 0


# debug_db = get_db(":memory:n")
# create = datetime.datetime.now().replace(microsecond=0)
# store_habit_item(debug_db, "some id", "debug 1", "user1", create, 4, "tomorrow")
# store_habit_item(debug_db, "some other id", "debug 2", "user1", create, 6, "today")
# # store_habit_item(debug_db, "debug 3", "user1", create, 1, "yesterday", False)
# print(get_all_habit_items(debug_db, "user1", True))
#
# store_task_item(debug_db, create, "some id")
# store_task_item(debug_db, create, "some id")
# store_task_item(debug_db, create, "some id")
# print(get_tasks_by_habit_id(debug_db, "some id"))

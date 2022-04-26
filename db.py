import sqlite3
import uuid
from custom_exceptions import HabitNameIsUnknownError, HabitNameAlreadyExistsError


def get_db(name="main.db"):
    db = sqlite3.connect(name)
    __create_tables(db)
    return db


def __create_tables(db):
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS habits (
        habit_id INT PRIMARY KEY,
        name TEXT,
        user_name TEXT,
        period INT,
        deadline DATETIME,
        current INT,
        longest INT
        )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INT,
        user_name TEXT,
        password TEXT,
        FOREIGN KEY (user_name) REFERENCES habits(user_name)
        )""")
    db.commit()


def store_habit_item(db, name, user_name, period, deadline, current=0, longest=0):
    if not __check_for_habit_item(db, name, user_name):
        cur = db.cursor()
        cur.execute("""INSERT INTO habits VALUES (
            :habit_id, :name, :user_name, :period, :deadline, :current, :longest)""",
                    {
                        "habit_id": str(uuid.uuid4()),
                        "name": name,
                        "user_name": user_name,
                        "period": period,
                        "deadline": deadline,
                        "current": current,
                        "longest": longest
                    })
        db.commit()
    else:
        raise HabitNameAlreadyExistsError


def delete_habit_item(db, name, user_name):
    if __check_for_habit_item(db, name, user_name):
        cur = db.cursor()
        cur.execute("DELETE FROM habits WHERE name=:name AND user_name=:user_name",
                    {
                        "name": name,
                        "user_name": user_name
                    })
        db.commit()
    else:
        raise HabitNameIsUnknownError


def update_habit_item(db, name, user_name, deadline, current, longest):
    cur = db.cursor()
    cur.execute("""UPDATE habits SET deadline=:deadline, current=:current, longest=:longest 
                   WHERE name=:name AND user_name=:user_name""",
                {
                    "name": name,
                    "user_name": user_name,
                    "deadline": deadline,
                    "current": current,
                    "longest": longest
                })
    db.commit()


def get_all_habit_items(db, user_name):
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE user_name=:user_name", {"user_name": user_name})
    return cur.fetchall()


def get_habit_item_by_name(db, name, user_name):
    if __check_for_habit_item(db, name, user_name):
        cur = db.cursor()
        cur.execute("SELECT * FROM habits WHERE name=:name AND user_name=:user_name",
                    {
                        "name": name,
                        "user_name": user_name
                    })
        return cur.fetchall()
    else:
        return None


def __check_for_habit_item(db, name, user_name):
    """Helper function that checks if the habit name is present in the database"""
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE name=:name AND user_name=:user_name",
                {
                    "name": name,
                    "user_name": user_name
                })
    return len(cur.fetchall()) != 0


# debug_db = get_db(":memory:n")
# store_habit_item(debug_db, "debug 1", "user1", 4, "tomorrow")
# store_habit_item(debug_db, "debug 2", "user1", 6, "today")
# print(get_all_habit_items(debug_db, "user1"))

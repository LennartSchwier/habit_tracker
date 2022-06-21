"""
Controls all database functionalities.

Functions:
    get_db(name="main.db") -> sqlite3 database
    store_user_item(db, user_name, password, is_admin)
    delete_user_item(db, user_name)
    get_user_item_by_name(db, user_name) -> list
    get_all_user_items(db) -> list
    store_habit_item(db, habit_id, name, user_name, created, period, deadline, is_active=True, longest=0)
    delete_habit_item(db, name, user_name)
    update_streaks_habit_item(db, name, user_name, deadline, longest)
    update_active_status_habit_item(db, name, user_name, deadline, is_active)
    get_all_habit_items(db, user_name, is_active) -> list
    get_habit_item_by_name(db, name, user_name) -> list
    store_task_item(db, created, habit_name)
    get_tasks_by_habit_name(db, habit_name) -> list
    remove_tasks_by_habit_name(db, habit_name)
"""

import sqlite3
import uuid
from custom_exceptions import UserNameAlreadyExistsError, UserNameIsUnknownError, \
    HabitNameIsUnknownError, HabitNameAlreadyExistsError


def get_db(name="main.db"):
    """
    Returns sqlite3 database with the necessary tables.

    Param:
        name (str): Name of the database (Default: main.db)

    Return:
        db (sqlite3 database): Database with tables "habits", "users" and "tasks"
    """
    db = sqlite3.connect(name)
    __create_tables(db)
    return db


def store_user_item(db, user_name, password, is_admin):
    """
    Inserts a new user item into "users" table or raises an exception if the user item already exists.

    Params:
        db: Database for storage
        user_name: Username to be stored
        password: Users password stored as a sh3_256 hash
        is_admin: True if user shall be stored as admin

    Raise:
        UserNameAlreadyExistsError: Raised if the user item is already in the database
    """
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
    """
    Deletes a user item from the "users" table or raises an exception if the user item does not exist.

    Params:
        db: Database from which the user item shall be deleted
        user_name: Username of the user item

    Raise:
        UserNameIsUnknownError: Raised if the user item does not exist in the database
    """
    if __is_user_item_stored(db, user_name):
        cur = db.cursor()
        cur.execute("DELETE FROM users WHERE user_name=:user_name", {"user_name": user_name})
        db.commit()
    else:
        raise UserNameIsUnknownError


def get_user_item_by_name(db, user_name):
    """
    Returns a user item by username if user exists otherwise None is returned.

    Params:
        db: Database from which the user item shall be returned
        user_name: Username to find user item in database

    Return:
        User item in a list if user exists otherwise None is returned
    """
    if __is_user_item_stored(db, user_name):
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE user_name=:user_name", {"user_name": user_name})
        return cur.fetchall()
    else:
        return None


def get_all_user_items(db):
    """
    Returns a list with all stored user items.

    Param:
        db: Database from which the user items shall be returned

    Return:
        List with all stored user items
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    return cur.fetchall()


def store_habit_item(db, habit_id, name, user_name, created, period, deadline, is_active=True, longest=0):
    """
    Stores a new habit item or raises an exception if a habit item with the same name is already in the database.

    Params:
        db: Database in which the habit shall be stored
        habit_id: Random UUID of the habit item
        name: Name of the habit item as provided by user
        user_name: Username of the storing user
        created: Datetime of creation
        period: Repetition period in days
        deadline: Datetime of the deadline
        is_active: Boolean if the habit is active or paused
        longest: Longest stored streak in days

    Raise:
        HabitNameAlreadyExistsError: Raised if a habit with the same name already exists
    """
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
    """
    Deletes a habit item or raises an exception if the name of the habit does not exist in the database.

    Params:
        db: Database from which the habit item shall be deleted
        name: Name of the habit item
        user_name: Username to verify the correct user deletes a habit

    Raise:
        HabitNameIsUnknownError: Raised if no habit item with the given name is stored
    """
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
    """
    Updates the deadline and streak of a habit item.

    Params:
        db: Database in which the habit item is stored
        name: Name of the habit item
        user_name: Username to verify the correct user updates a habit item
        deadline: Datetime of the new deadline
        longest: Longest streak of the habit item
    """
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
    """
    Sets the active status of a habit item to active or inactive.

    Params:
        db: Database in which the habit item is stored
        name: Name of the habit item
        user_name: Username to verify the correct user updates the habit item
        deadline: Sets the deadline according to the active status
        is_active: Boolean for the active status
    """
    cur = db.cursor()
    cur.execute("UPDATE habits SET deadline=:deadline, is_active=:is_active WHERE name=:name AND user_name=:user_name",
                {
                    "name": name,
                    "user_name": user_name,
                    "deadline": deadline,
                    "is_active": is_active
                })
    db.commit()


def get_all_habit_items_by_active_status(db, user_name, is_active):
    """
    Returns a list with all habit items with a given active status stored for a particular user.

    Params:
        db: Database in which the habit items are stored
        user_name: The user who has stored the habit items
        is_active: Only the habit items with the given active status are selected

    Return:
        List with all habit items with a given active status stored for a particular user
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE user_name=:user_name AND is_active=:is_active",
                {
                    "user_name": user_name,
                    "is_active": is_active
                })
    return cur.fetchall()


def get_habit_item_by_name(db, name, user_name):
    """
    Returns a list with a habit item if it exists otherwise None is returned.

    Param:
        db: Database in which the habit item is stored
        name: Name of the habit item
        user_name: Only the habit items of this user are regarded

    Return:
        List with habit item or None if name of habit item does not exist
    """
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
    """
    Assigns a random UUID to a new task item and stores it in the "tasks" table.

    Params:
        db: Database in which the task item is stored
        created: Datetime of the creation
        habit_name: The name of the habit item to which the task belongs
    """
    cur = db.cursor()
    cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
                {
                    "task_id": str(uuid.uuid4()),
                    "created": created,
                    "habit_name": habit_name
                })
    db.commit()


def get_tasks_by_habit_name(db, habit_name):
    """
    Returns a list with all task items that belong to a given habit item.

    Params:
        db: Database in which the task items are stored
        habit_name: Name of the habit item from which the tasks shall be retrieved

    Return:
        List with all task items of the given habit item
    """
    cur = db.cursor()
    cur.execute("SELECT * FROM tasks WHERE habit_name=:habit_name", {"habit_name": habit_name})
    return cur.fetchall()


def remove_tasks_by_habit_name(db, habit_name):
    """
    Removes all stored task items of a given habit item.

    Params:
        db: Database in which the task items are stored
        habit_name: Name of the habit item from which the task items hall be removed
    """
    cur = db.cursor()
    cur.execute("DELETE FROM tasks WHERE habit_name=:habit_name", {"habit_name": habit_name})
    db.commit()


def __create_tables(db):
    # Creates tables in database
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
    # Checks if the username is present in the database
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE user_name=:user_name", {"user_name": user_name})
    return len(cur.fetchall()) != 0


def __is_habit_item_stored(db, name, user_name):
    # Checks if the habit name is present in the database
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

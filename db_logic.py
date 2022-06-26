"""
Contains the logic to access all database functionalities related to habit and task management.

Functions:
    connect_to_db(name="main.db")
        Connects to a sqlite3 database.
    get_habit_by_name(db, name: str, user_name: str) -> Habit
        Receives the habit item from the database by name and returns it as a Habit instance.
    get_all_habits(db, user_name: str, is_active: bool) -> list
        Receives all habit items stored for a particular user with a given active status
        and returns them in a list of Habit instances.
    add_habit(db, habit: Habit, user_name: str)
        Takes a Habit instance and stores it as a habit item in a database.
    remove_habit(db, name: str, user_name: str)
        Removes a single habit item by name and all tasks associated to this habit.
    get_all_tasks(db, habit_name: str)
        Receives all tasks stored for a given habit and returns them in a list of Task instances.
    update_streaks(db, name: str, user_name: str)
        Updates the stored streak of a habit according to the deadline.
    update_active_status(db, name: str, user_name: str, new_active_status: bool)
"""
from db import store_habit_item, delete_habit_item, get_habit_item_by_name, \
    update_streaks_habit_item, get_db, get_all_habit_items_by_active_status, store_task_item, get_tasks_by_habit_name, \
    remove_tasks_by_habit_name, update_active_status_habit_item
from habit import Habit
from task import Task
from datetime import datetime


def connect_to_db(name="main.db"):
    """
    Connects to a sqlite3 database.

    Param:
        name: str
            Sets the name of the database (default is "main.db")

    Return:
        sqlite3 db
    """
    return get_db(name)


def get_habit_by_name(db, name: str, user_name: str) -> Habit or None:
    """
    Receives the habit item from the database by name and returns it as a Habit instance.

    Params:
        db: str
            Name of the database where the habit is stored
        name: str
            Name of the habit
        user_name: str
            Name of the user who has stored the habit

    Return:
        Habit instance if habit item is stored, otherwise None
    """
    if get_habit_item_by_name(db, name, user_name) is None:
        return None
    else:
        habit_item = get_habit_item_by_name(db, name, user_name)[0]
        return Habit(
            habit_id=habit_item[0],
            name=habit_item[1],
            created=habit_item[3],
            period=habit_item[4],
            deadline=datetime.strptime(habit_item[5], "%Y-%m-%d %H:%M:%S"),
            is_active=habit_item[6] == 1,
            current_streak=len(get_tasks_by_habit_name(db, habit_item[1])),

            longest_streak=habit_item[7]
        )


def get_all_habits(db, user_name: str, is_active: bool) -> list:
    """
    Receives all habit items stored for a particular user with a given active status
    and returns them in a list of Habit instances.

    Params:
        db: str
            Name of the database that contains the habit items
        user_name: str
            Name of the user for which the habits shall be retrieved
        is_active: bool
            Filters only active or inactive habits

    Return:
        all_habits: list
            A list containing all received Habit instances, can be empty
    """
    all_habits = []
    for habit_item in get_all_habit_items_by_active_status(db, user_name, is_active):
        habit = Habit(
            habit_id=habit_item[0],
            name=habit_item[1],
            created=habit_item[3],
            period=habit_item[4],
            deadline=datetime.strptime(habit_item[5], "%Y-%m-%d %H:%M:%S"),
            is_active=habit_item[6] == 1,
            current_streak=len(get_tasks_by_habit_name(db, habit_item[1])),
            longest_streak=habit_item[7]
        )
        all_habits.append(habit)
    return all_habits


def add_habit(db, habit: Habit, user_name: str):
    """
    Takes a Habit instance and stores it as a habit item in a database.

    Params:
        db: str
            Name of the database in which the habit shall be stored
        habit: Habit
            The Habit instance to be stored
        user_name:
            Name of the user who stores the habit
    """
    created = datetime.now().replace(microsecond=0)
    store_habit_item(db, habit.habit_id, habit.name, user_name, created, habit.period, habit.deadline)


def remove_habit(db, name: str, user_name: str):
    """
    Removes a single habit item by name and all tasks associated to this habit.

    Params:
        db: str
            Name of the database in which the habit is stored
        name: str
            Name of the habit item that shall be removed
        user_name: str
            Name of the user to verify the correct habit is removed
    """
    delete_habit_item(db, name, user_name)
    remove_tasks_by_habit_name(db, name)


def get_all_tasks(db, habit_name: str) -> list:
    """
    Receives all tasks stored for a given habit and returns them in a list of Task instances.

    Params:
        db: str
            Name of the database in which the tasks are stored
        habit_name: str
            Name of the habit to which the tasks are associated

    Return:
        all_tasks: list
            A list with Task instances, can be empty
    """
    all_tasks = []
    for task_item in get_tasks_by_habit_name(db, habit_name):
        task = Task(
            task_id=task_item[0],
            created=task_item[1]
        )
        all_tasks.append(task)
    return all_tasks


def update_streaks(db, name: str, user_name: str):
    """
    Updates the stored streak of a habit according to the deadline.

    If the task was completed within the deadline,
    the current streak is increased by one and the task will be stored in the database. If not,
    the current streak is set to zero and all associated tasks are deleted.

    Params:
    db: str
        Name of the database in which the habit is stored
    name: str
        Name of the habit that shall be updated
    user_name: str
        Name of the user to which the habit belongs
    """
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.complete_task()
    if habit_entity.current_streak == 0:
        remove_tasks_by_habit_name(db, habit_entity.habit_id)
    else:
        update_streaks_habit_item(db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.longest_streak)
        store_task_item(db, datetime.now().replace(microsecond=0), habit_entity.name)


def update_active_status(db, name: str, user_name: str, new_active_status: bool):
    """
    Sets the active status of a habit to active or inactive and stores the new status in the database.

    Params:
        db: str
            Name of the database in which the habit is stored
        name: str
            Name of the habit that shall be updated
        user_name: str
            Name of the user to which the habit belongs
    """
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.set_active_status(new_active_status)
    update_active_status_habit_item(db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.is_active)

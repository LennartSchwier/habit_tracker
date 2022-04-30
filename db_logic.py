from db import store_habit_item, delete_habit_item, get_habit_item_by_name, \
    update_streaks_habit_item, get_db, get_all_habit_items, store_task_item, get_tasks_by_habit_name, \
    remove_tasks_by_habit_name, update_active_status_habit_item
from habit import Habit
from task import Task
from datetime import datetime


def connect_to_db(name="main.db"):
    return get_db(name)


def get_habit_by_name(db, name: str, user_name: str):
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


def get_all_habits(db, user_name: str, is_active: bool):
    all_habits = []
    for habit_item in get_all_habit_items(db, user_name, is_active):
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
    created = datetime.now().replace(microsecond=0)
    store_habit_item(db, habit.habit_id, habit.name, user_name, created, habit.period, habit.deadline)


def remove_habit(db, name: str, user_name: str):
    delete_habit_item(db, name, user_name)
    remove_tasks_by_habit_name(db, name)


def get_all_tasks(db, habit_name: str):
    all_tasks = []
    for task_item in get_tasks_by_habit_name(db, habit_name):
        task = Task(
            task_id=task_item[0],
            created=task_item[1]
        )
        all_tasks.append(task)
    return all_tasks


def update_streaks(db, name: str, user_name: str):
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.complete_task()
    if habit_entity.current_streak == 0:
        remove_tasks_by_habit_name(db, habit_entity.habit_id)
    else:
        update_streaks_habit_item(db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.longest_streak)
        store_task_item(db, datetime.now().replace(microsecond=0), habit_entity.name)


def update_active_status(db, name: str, user_name: str, new_active_status: bool):
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.set_active_status(new_active_status)
    update_active_status_habit_item(db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.is_active)

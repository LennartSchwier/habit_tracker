from db import store_habit_item, delete_habit_item, get_habit_item_by_name, \
    update_habit_item, get_db, get_all_habit_items
from habit import Habit
from datetime import datetime


def connect_to_db(name="main.db"):
    return get_db(name)


def get_habit_by_name(db, name: str, user_name: str):
    habit_item = get_habit_item_by_name(db, name, user_name)
    if habit_item is not None:
        return Habit(
            name=habit_item[0][1],
            period=habit_item[0][3],
            deadline=datetime.strptime(habit_item[0][4], "%Y-%m-%d %H:%M:%S"),
            is_active=habit_item[0][5] == 1,
            current_streak=habit_item[0][6],
            longest_streak=habit_item[0][7]
        )
    else:
        return None


def get_all_habits(db, user_name: str, is_active: bool):
    all_habits = []
    for item in get_all_habit_items(db, user_name, is_active):
        habit = Habit(item[1], item[3], datetime.strptime(item[4], "%Y-%m-%d %H:%M:%S"), item[5], item[6], item[7])
        all_habits.append(habit)
    return all_habits


def add_habit(db, habit: Habit, user_name: str):
    store_habit_item(db, habit.name, user_name, habit.period, habit.deadline)


def remove_habit(db, name: str, user_name: str):
    delete_habit_item(db, name, user_name)


def update_habit_streaks(db, name: str, user_name: str):
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.complete_task()
    update_habit_item(
        db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.is_active,
        habit_entity.current_streak, habit_entity.longest_streak
    )


def update_active_status(db, name: str, user_name: str, is_active: bool):
    habit_entity = get_habit_by_name(db, name, user_name)
    habit_entity.set_active_status(is_active)
    update_habit_item(db, habit_entity.name, user_name, habit_entity.deadline, habit_entity.is_active,
                      habit_entity.current_streak, habit_entity.longest_streak)

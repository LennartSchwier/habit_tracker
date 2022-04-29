import sqlite3
import os

import pytest

from habit import Habit
from user import User
from user_logic import get_user_by_name, add_user, remove_user, get_all_users, validate_password
from db_logic import connect_to_db, add_habit, remove_habit, update_streaks, get_habit_by_name, get_all_habits, \
    update_active_status
from analysis import analyse_habits
from custom_exceptions import HabitNameAlreadyExistsError, MissingAuthorizationError
from datetime import datetime, timedelta


class TestHabits:
    created = datetime.strptime("2022-04-21 18:00:00", "%Y-%m-%d %H:%M:%S")
    deadline = datetime.strptime("2032-04-21 18:00:00", "%Y-%m-%d %H:%M:%S")

    def setup_method(self):
        self.db = connect_to_db("test.db")
        cur = self.db.cursor()

        # Inserting a test user and a test admin into the database users table
        cur.execute("""INSERT INTO users VALUES (
                    :user_id, :user_name, :password, :is_admin)""",
                    {
                        "user_id": "some id",
                        "user_name": "test user",
                        "password": "some password",
                        "is_admin": "False"
                    })
        cur.execute("""INSERT INTO users VALUES (
                    :user_id, :user_name, :password, :is_admin)""",
                    {
                        "user_id": "some id",
                        "user_name": "test admin",
                        "password": "some password",
                        "is_admin": "True"
                    })

        # Inserting five different habits into the database habits table
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": "some id",
                        "name": "first habit",
                        "user_name": "test user",
                        "created": self.created,
                        "period": 2,
                        "deadline": self.deadline,
                        "is_active": True,
                        "longest": 7
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": "some other id",
                        "name": "second habit",
                        "user_name": "test user",
                        "created": self.created,
                        "period": 5,
                        "deadline": self.deadline,
                        "is_active": True,
                        "longest": 9
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": "another id",
                        "name": "third habit",
                        "user_name": "test user",
                        "created": self.created,
                        "period": 2,
                        "deadline": self.deadline,
                        "is_active": True,
                        "longest": 0
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": "different user id",
                        "name": "different user habit",
                        "user_name": "different user",
                        "created": self.created,
                        "period": 1,
                        "deadline": self.deadline,
                        "is_active": True,
                        "longest": 0
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :created, :period, :deadline, :is_active, :longest)""",
                    {
                        "habit_id": "inactive id",
                        "name": "inactive habit",
                        "user_name": "test user",
                        "created": self.created,
                        "period": 2,
                        "deadline": self.deadline,
                        "is_active": False,
                        "longest": 83
                    })
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_id)",
                    {
                        "task_id": "1",
                        "created": self.created,
                        "habit_id": "some id"
                    })
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_id)",
                    {
                        "task_id": "2",
                        "created": self.created,
                        "habit_id": "some id"
                    })
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_id)",
                    {
                        "task_id": "1",
                        "created": self.created,
                        "habit_id": "some other id"
                    })
        self.db.commit()

    def test_habit_class(self):

        test_habit = Habit(
            habit_id="some id",
            name="habit class test",
            created=self.created,
            period=4,
            deadline=self.deadline,
            is_active=True
        )

        # Test that length_of_streak param is updated correctly
        test_habit.complete_task()
        assert test_habit.current_streak is 1 and test_habit.longest_streak is 1

        # Test that is_active status and deadline is updated correctly
        test_habit.set_active_status(False)
        assert test_habit.is_active is False
        assert test_habit.deadline == datetime.max - timedelta(microseconds=999999)
        test_habit.set_active_status(True)
        assert test_habit.deadline is not datetime.max

        # Test that a period less than one raises an AssertionError
        try:
            Habit(
                habit_id="some id",
                name="invalid period habit",
                created=self.created,
                period=0,
                deadline=self.deadline,
                is_active=True)
        except AssertionError:
            pass
        else:
            pytest.fail()

    def test_user_logic(self):

        # Test that the correct user item is received from database
        received_object = get_user_by_name(self.db, "test user")
        assert type(received_object) is User and received_object.user_name == "test user"

        # Test that the user is added to the database
        another_user = User("some other user", "some password", False)
        add_user(self.db, another_user)
        received_object = get_user_by_name(self.db, another_user.user_name)
        assert type(received_object) is User and received_object.user_name == "some other user"

        # Test that a list with all stored users is returned
        all_users = get_all_users(self.db)
        assert type(all_users) is list and len(all_users) is 3

        # Test that an exception is raised when non-admin tries to delete user
        try:
            remove_user(self.db, "test user", "some other user")
        except MissingAuthorizationError:
            pass
        else:
            pytest.fail()

        # Test that the user is removed from database
        remove_user(self.db, "test admin", "some other user")
        assert len(get_all_users(self.db)) is 2

        # Test that correct boolean is returned
        assert validate_password(self.db, "test user", "some password") is True
        assert validate_password(self.db, "test user", "incorrect password") is False

    def test_db_logic(self):

        assert type(self.db) is sqlite3.Connection

        # Test that the correct habit item is received from database
        received_object = get_habit_by_name(self.db, "first habit", "test user")
        assert type(received_object) is Habit and received_object.name == "first habit"
        assert received_object.current_streak is 2 and received_object.longest_streak is 7

        # Test that the correct list with all stored habits is received from database
        all_active_habits = get_all_habits(self.db, "test user", True)
        assert type(all_active_habits) is list and len(all_active_habits) is 3
        all_inactive_habits = get_all_habits(self.db, "test user", False)
        assert type(all_inactive_habits) is list and len(all_inactive_habits) is 1

        # Test that the habit is added to the database
        test_habit = Habit(
            habit_id="habit id",
            name="test habit",
            created=self.created,
            period=4,
            deadline=self.deadline,
            is_active=True)
        add_habit(self.db, test_habit, "test user")
        received_object = get_habit_by_name(self.db, test_habit.name, "test user")
        assert type(received_object) is Habit and received_object.name == "test habit"
        assert len(get_all_habits(self.db, "test user", True)) is 4

        # Test that adding a habit with the same name raises a HabitNameAlreadyExistsError
        try:
            add_habit(self.db, test_habit, "test user")
        except HabitNameAlreadyExistsError:
            pass
        else:
            pytest.fail()

        # Test that the habit is updated correctly (deadline and longest_streak)
        assert test_habit.deadline is self.deadline
        assert test_habit.current_streak is 0 and test_habit.longest_streak is 0
        update_streaks(self.db, test_habit.name, "test user")
        received_object = get_habit_by_name(self.db, test_habit.name, "test user")
        assert received_object.deadline == self.deadline + timedelta(days=test_habit.period)
        assert received_object.current_streak is 1 and received_object.longest_streak is 1

        # Test that a paused habit is set inactive in the database
        update_active_status(self.db, test_habit.name, "test user", False)
        received_object = get_habit_by_name(self.db, test_habit.name, "test user")
        assert received_object.is_active is False
        assert received_object.deadline == datetime.max - timedelta(microseconds=999999)
        assert len(get_all_habits(self.db, "test user", False)) is 2
        assert len(get_all_habits(self.db, "test user", True)) is 3
        # update_active_status(self.db, received_object.name, "test_user", True)
        # received_object = get_habit_by_name(self.db, received_object.name, "test user")
        # assert received_object.is_active is False

        # Test that habit is removed from database
        remove_habit(self.db, test_habit.name, "test user")
        removed_habit = get_habit_by_name(self.db, test_habit.name, "test user")
        assert removed_habit is None
        all_active_habits = get_all_habits(self.db, "test user", True)
        assert len(all_active_habits) is 3

        # TODO Test that removing a non-existent habit raises a HabitIsUnknownError

    def test_analysis(self):

        # Test that a list with all active habits and its associated details is returned
        active_habits = get_all_habits(self.db, "test user", True)
        choice = "Currently tracked habits."
        output = analyse_habits(choice, active_habits=active_habits)
        assert output == ['first habit. Period: 2 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '2. Longest streak: 7.',
                          'second habit. Period: 5 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '1. Longest streak: 9.',
                          'third habit. Period: 2 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '0. Longest streak: 0.']

        # Test that a list with all paused habits and its associated details is returned
        inactive_habits = get_all_habits(self.db, "test user", False)
        choice = "Paused habits."
        output = analyse_habits(choice, inactive_habits=inactive_habits)
        assert output == ['inactive habit. Period: 2 days. Current streak: 0. Longest streak: 83.']

        # Test that a list with all habits with period 2 is returned
        choice = "All habits with same period."
        output = analyse_habits(choice, active_habits=active_habits, period=2)
        assert output == ['first habit', 'third habit']

        # Test that the habit with the longest streak is returned
        choice = "Habit with longest streak."
        output = analyse_habits(choice, active_habits=active_habits)
        assert output == ["second habit with 9 times"]

    @staticmethod
    def teardown_method():
        os.remove("test.db")

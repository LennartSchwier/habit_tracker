"""
Contains all unit tests for the entire project with pytest as testing library.

Class:
    TestHabits
"""
import sqlite3
import os

import pytest

from habit import Habit
from user import User
from user_logic import get_user_by_name, add_user, remove_user, get_all_users, validate_password
from db_logic import connect_to_db, add_habit, remove_habit, update_streaks, get_habit_by_name, get_all_habits, \
    update_active_status, get_all_tasks
from analysis import analyse_habits
from custom_exceptions import HabitNameAlreadyExistsError, MissingAuthorizationError, HabitNameIsUnknownError
from datetime import datetime, timedelta


class TestHabits:
    """
    Pytest testing class for all unit tests.

    Methods:
        setup_method()
            Creates test database with one user, one admin, and five different habits.
        test_habit_class()
            Tests functionalities of the Habit class.
        test_user_logic()
            Tests functionalities of the user_logic module.
        test_db_logic()
            Tests functionalities of the db_logic module.
        test_analysis()
            Tests functionalities of the analysis module.
        teardown_method()
            Removes the test database file from the system.
    """
    created = datetime.strptime("2022-04-21 18:00:00", "%Y-%m-%d %H:%M:%S")
    deadline = datetime.strptime("2032-04-21 18:00:00", "%Y-%m-%d %H:%M:%S")

    def setup_method(self):
        """Creates test database with one user, one admin, and five different habits."""
        self.db = connect_to_db("test.db")
        cur = self.db.cursor()

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
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
                    {
                        "task_id": "1",
                        "created": self.created,
                        "habit_name": "first habit"
                    })
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
                    {
                        "task_id": "2",
                        "created": self.created,
                        "habit_name": "first habit"
                    })
        cur.execute("INSERT INTO tasks VALUES (:task_id, :created, :habit_name)",
                    {
                        "task_id": "1",
                        "created": self.created,
                        "habit_name": "second habit"
                    })
        self.db.commit()

    def test_habit_class(self):
        """Tests functionalities of the Habit class."""

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
        assert test_habit.current_streak == 1 and test_habit.longest_streak == 1

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
        """Tests functionalities of the user_logic module."""

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
        assert type(all_users) == list and len(all_users) == 3

        # Test that an exception is raised when non-admin tries to delete user
        try:
            remove_user(self.db, "test user", "some other user")
        except MissingAuthorizationError:
            pass
        else:
            pytest.fail()

        # Test that the user is removed from database
        remove_user(self.db, "test admin", "some other user")
        assert len(get_all_users(self.db)) == 2

        # Test that correct boolean is returned
        assert validate_password(self.db, "test user", "some password") is True
        assert validate_password(self.db, "test user", "incorrect password") is False

    def test_db_logic(self):
        """Tests functionalities of the db_logic module."""

        assert type(self.db) is sqlite3.Connection

        # Test that the correct habit item is received from database
        received_object = get_habit_by_name(self.db, "first habit", "test user")
        assert type(received_object) is Habit and received_object.name == "first habit"
        assert received_object.current_streak == 2 and received_object.longest_streak == 7

        # Test that the correct list with all stored habits is received from database
        all_active_habits = get_all_habits(self.db, "test user", True)
        assert type(all_active_habits) == list and len(all_active_habits) == 3
        all_inactive_habits = get_all_habits(self.db, "test user", False)
        assert type(all_inactive_habits) == list and len(all_inactive_habits) == 1

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
        assert len(get_all_habits(self.db, "test user", True)) == 4

        # Test that adding a habit with the same name raises a HabitNameAlreadyExistsError
        try:
            add_habit(self.db, test_habit, "test user")
        except HabitNameAlreadyExistsError:
            pass
        else:
            pytest.fail()

        # Test that the longest streak of the habit is updated correctly
        assert test_habit.deadline is self.deadline
        assert test_habit.current_streak == 0 and test_habit.longest_streak == 0
        update_streaks(self.db, test_habit.name, "test user")
        received_object = get_habit_by_name(self.db, test_habit.name, "test user")
        assert received_object.current_streak == 1 and received_object.longest_streak == 1

        # Test that the habit active status is changed to inactive in the database
        update_active_status(self.db, test_habit.name, "test user", False)
        received_object = get_habit_by_name(self.db, test_habit.name, "test user")
        assert received_object.is_active is False
        assert received_object.deadline == datetime.max - timedelta(microseconds=999999)
        assert len(get_all_habits(self.db, "test user", False)) == 2
        assert len(get_all_habits(self.db, "test user", True)) == 3

        # Test that the habit active status is changed to active in the database
        update_active_status(self.db, received_object.name, "test user", True)
        received_object = get_habit_by_name(self.db, received_object.name, "test user")
        assert received_object.is_active is True
        assert len(get_all_habits(self.db, "test user", False)) == 1
        assert len(get_all_habits(self.db, "test user", True)) == 4

        # Test that habit is removed from database
        remove_habit(self.db, test_habit.name, "test user")
        removed_habit = get_habit_by_name(self.db, test_habit.name, "test user")
        assert removed_habit is None
        all_active_habits = get_all_habits(self.db, "test user", True)
        assert len(all_active_habits) == 3

        # Test that removing a non-existent habit raises a HabitIsUnknownError
        try:
            remove_habit(self.db, "non existing habit", "test user")
        except HabitNameIsUnknownError:
            pass
        else:
            pytest.fail()

        # Test that all completed tasks for a habit are received from database
        received_tasks = get_all_tasks(self.db, "first habit")
        assert type(received_tasks) is list and len(received_tasks) == 2

    def test_analysis(self):
        """Tests functionalities of the analysis module."""

        # Test that a list with all active habits and its associated details is returned
        active_habits = get_all_habits(self.db, "test user", True)
        choice = "Currently tracked habits."
        output = analyse_habits(choice, active_habits=active_habits)
        assert output == ['first habit:\n'
                          '            Created: 2022-04-21 18:00:00. Period: 2 days. Deadline: '
                          '2032-04-21 18:00:00. \n'
                          '            Current streak: 2. Longest streak: 7.\n'
                          '            ------------------------------------------',
                          'second habit:\n'
                          '            Created: 2022-04-21 18:00:00. Period: 5 days. Deadline: '
                          '2032-04-21 18:00:00. \n'
                          '            Current streak: 1. Longest streak: 9.\n'
                          '            ------------------------------------------',
                          'third habit:\n'
                          '            Created: 2022-04-21 18:00:00. Period: 2 days. Deadline: '
                          '2032-04-21 18:00:00. \n'
                          '            Current streak: 0. Longest streak: 0.\n'
                          '            ------------------------------------------']

        # Test that a list with all paused habits and its associated details is returned
        inactive_habits = get_all_habits(self.db, "test user", False)
        choice = "Paused habits."
        output = analyse_habits(choice, inactive_habits=inactive_habits)
        assert output == ['inactive habit: \n'
                          '            Period: 2 days. \n'
                          '            Current streak: 0. Longest streak: 83.\n'
                          '            ------------------------------------------']

        # Test that a list with all habits with period 2 is returned
        choice = "All habits with same period."
        output = analyse_habits(choice, active_habits=active_habits, period=2)
        assert output == ['first habit', 'third habit']

        # Test that the habit with the longest streak is returned
        choice = "Habit with longest streak."
        output = analyse_habits(choice, active_habits=active_habits)
        assert output == ["second habit with 9 times"]

        # Test that all completed tasks for a habit are returned
        completed_tasks = get_all_tasks(self.db, "first habit")
        choice = "Completed tasks."
        output = analyse_habits(choice, completed_tasks=completed_tasks)
        assert output == ['1. Task. Completed on: 2022-04-21 18:00:00', '2. Task. Completed on: 2022-04-21 18:00:00']

    #
    @staticmethod
    def teardown_method():
        """Removes the test database file from the system."""
        os.remove("test.db")

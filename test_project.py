import sqlite3
import os
from habit import Habit
from db_logic import connect_to_db, add_habit, remove_habit, update_habit_streaks, get_habit_by_name, get_all_habits
from analysis import analyse_habits
from custom_exceptions import HabitNameAlreadyExistsError
from datetime import datetime, timedelta


class TestHabits:
    deadline = datetime.strptime("2032-04-21 18:00:00", "%Y-%m-%d %H:%M:%S")

    def setup_method(self):
        self.db = connect_to_db("test.db")
        cur = self.db.cursor()
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :period, :deadline, :current, :longest)""",
                    {
                        "habit_id": "some id",
                        "name": "first habit",
                        "user_name": "test_user",
                        "period": 2,
                        "deadline": self.deadline,
                        "current": 4,
                        "longest": 7
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :period, :deadline, :current, :longest)""",
                    {
                        "habit_id": "some other id",
                        "name": "second habit",
                        "user_name": "test_user",
                        "period": 5,
                        "deadline": self.deadline,
                        "current": 2,
                        "longest": 9
                    })
        cur.execute("""INSERT INTO habits VALUES (
                    :habit_id, :name, :user_name, :period, :deadline, :current, :longest)""",
                    {
                        "habit_id": "another id",
                        "name": "third habit",
                        "user_name": "test_user",
                        "period": 2,
                        "deadline": self.deadline,
                        "current": 0,
                        "longest": 0
                    })
        cur.execute("""INSERT INTO habits VALUES (
                            :habit_id, :name, :user_name, :period, :deadline, :current, :longest)""",
                    {
                        "habit_id": "different user id",
                        "name": "different user habit",
                        "user_name": "different_user",
                        "period": 1,
                        "deadline": self.deadline,
                        "current": 0,
                        "longest": 0
                    })
        self.db.commit()

    def test_habit_class(self):

        test_habit = Habit("habit class test", 1, self.deadline)
        # Test Habit class constructor
        assert type(test_habit) is Habit
        assert test_habit.current_streak is 0 and test_habit.longest_streak is 0
        assert type(test_habit.deadline) is datetime

        # Test that length_of_streak param is updated
        test_habit.complete_task()
        assert test_habit.current_streak is 1 and test_habit.longest_streak is 1

        # Test that a period less than one raises an AssertionError
        try:
            Habit("invalid period habit", 0, self.deadline)
        except AssertionError:
            pass

    def test_db_logic(self):

        assert type(self.db) is sqlite3.Connection

        # Test that the correct habit item is received from database
        received_object = get_habit_by_name(self.db, "first habit", "test_user")
        assert type(received_object) is Habit and received_object.name == "first habit"
        assert received_object.current_streak is 4 and received_object.longest_streak is 7

        # Test that the habit is added to the database
        another_test_habit = Habit("another test habit", 4, self.deadline)
        add_habit(self.db, another_test_habit, "test_user")
        received_object = get_habit_by_name(self.db, "another test habit", "test_user")
        assert type(received_object) is Habit and received_object.name == another_test_habit.name

        # Test that adding a habit with the same name raises a HabitNameAlreadyExistsError
        try:
            add_habit(self.db, another_test_habit, "test_user")
        except HabitNameAlreadyExistsError:
            pass

        # Test that a list with all stored habits is received from database
        all_habits = get_all_habits(self.db, "test_user")
        assert type(all_habits) is list and len(all_habits) is 4

        # Test that the habit is updated correctly (deadline, current_streak and longest_streak)
        assert another_test_habit.deadline is self.deadline
        assert another_test_habit.current_streak is 0 and another_test_habit.longest_streak is 0
        update_habit_streaks(self.db, another_test_habit.name, "test_user")
        another_test_habit = get_habit_by_name(self.db, another_test_habit.name, "test_user")
        assert another_test_habit.deadline == self.deadline + timedelta(days=another_test_habit.period)
        assert another_test_habit.current_streak is 1 and another_test_habit.longest_streak is 1

        # Test that habit is removed from database
        remove_habit(self.db, another_test_habit.name, "test_user")
        removed_habit = get_habit_by_name(self.db, another_test_habit.name, "test_user")
        assert removed_habit is None
        all_habits = get_all_habits(self.db, "test_user")
        assert len(all_habits) is 3

        # TODO Test that removing a non-existent habit raises a HabitIsUnknownError

    def test_analysis(self):

        # Test that a list with all habits and its associated details is returned
        choice = "Show currently tracked habits."
        output = analyse_habits(self.db, choice, "test_user")
        assert output == ['first habit. Period: 2 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '4. Longest streak: 7.',
                          'second habit. Period: 5 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '2. Longest streak: 9.',
                          'third habit. Period: 2 days. Deadline: 2032-04-21 18:00:00. Current streak: '
                          '0. Longest streak: 0.']

        # Test that a list with all habits with period 2 is returned
        choice = "Show all habits with same period."
        output = analyse_habits(self.db, choice, "test_user", period=2)
        assert output == ['first habit', 'third habit']

        # Test that the habit with the longest streak is returned
        choice = "Show habit with longest streak."
        output = analyse_habits(self.db, choice, "test_user")
        assert output == ["second habit with 9 times"]

    @staticmethod
    def teardown_method():
        os.remove("test.db")

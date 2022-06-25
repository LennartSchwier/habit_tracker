"""Contains the Habit class."""
from datetime import datetime, timedelta
import uuid
from custom_exceptions import UpdateActiveStatusError


class Habit:
    """
    Class to represent a habit.

    Attributes:
        habit_id: UUID
            Unique ID to represent the habit
        name: str
            The name of the habit
        created: datetime
            Date and time of the creation
        period: int
            Periodicity in days
        deadline: datetime
            Date and time of the deadline
        is_active: bool
            Shows if habit is active or inactive
        current_streak: int
            Length of the current streak in days (default 0)
        longest_streak: int
            Length of the longest streak in days (default 0)

    Methods:
        complete_task()
            Updates deadline and streaks according to deadline
        set_active_status(is_active: bool)
            Updates the active status and sets the deadline accordingly
    """

    def __init__(self, habit_id: uuid, name: str, created: datetime, period: int, deadline: datetime,
                 is_active: bool, current_streak=0, longest_streak=0
                 ):
        """
        Constructor for a Habit instance.

        Params:
            habit_id: UUID
                Unique ID to represent the habit
            name: str
                The name of the habit
            created: datetime
                Date and time of the creation
            period: int
                Periodicity in days
            deadline: datetime
                Date and time of the deadline
            is_active: bool
                Shows if habit is active or inactive
            current_streak: int
                Length of the current streak in days (default 0)
            longest_streak: int
                Length of the longest streak in days (default 0)
        """
        assert period >= 1, f"Period {period} has to be greater or equal than one"

        self.habit_id = habit_id
        self.name = name
        self.created = created
        self.period = period
        self.deadline = deadline
        self.is_active = is_active
        self.current_streak = current_streak
        self.longest_streak = longest_streak

    def complete_task(self):
        """Updates deadline and streaks according to deadline."""
        if self.__is_within_deadline():
            self.current_streak += 1
            self.deadline += timedelta(days=self.period)
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0
            self.deadline += timedelta(days=self.period)

    def set_active_status(self, is_active: bool):
        """
        Updates the active status and sets the deadline accordingly.

        Param:
            is_active: bool
                Shows if habit is active or inactive

        Raise:
            UpdateActiveStatusError
                Raised if the update has failed
        """
        previous_status = self.is_active
        self.is_active = is_active
        new_status = self.is_active
        if previous_status is True and new_status is False:
            self.deadline = datetime.max - timedelta(microseconds=999999)
        elif previous_status is False and new_status is True:
            self.deadline = datetime.now().replace(microsecond=0) + timedelta(days=self.period)
        else:
            raise UpdateActiveStatusError

    def __is_within_deadline(self):
        # Returns True if deadline has not passed already.
        return datetime.now() <= self.deadline

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"('{self.name}, {self.created}, {self.period}, " \
               f"{self.is_active}, {self.current_streak}, {self.longest_streak}')"

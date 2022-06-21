from datetime import datetime, timedelta
import uuid
from custom_exceptions import UpdateActiveStatusError


class Habit:

    def __init__(self, habit_id: uuid, name: str, created: datetime, period: int, deadline: datetime,
                 is_active: bool, current_streak=0, longest_streak=0
                 ):
        assert period >= 1, f"Period {period} has to be greater or equal than one"

        # TODO private parameters, timezone
        self.habit_id = habit_id
        self.name = name
        self.created = created
        self.period = period
        self.deadline = deadline
        self.is_active = is_active
        self.current_streak = current_streak
        self.longest_streak = longest_streak

    def complete_task(self):
        """Updates deadline and streaks according to deadline"""
        if self.__is_within_deadline():
            self.current_streak += 1
            self.deadline += timedelta(days=self.period)
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0

    def set_active_status(self, is_active: bool):
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
        """Private method that returns 'True' if deadline has not passed already"""
        return datetime.now() <= self.deadline

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"('{self.name}, {self.created}, {self.period}, " \
               f"{self.is_active}, {self.current_streak}, {self.longest_streak}')"

"""Contains the Task class"""
import uuid
import datetime


class Task:
    """
    Class to represent a task.

    Attributes:
        task_id: UUID
            Unique ID to represent the task
        created: datetime
            Tha date and time of creation of the task
    """

    def __init__(self, task_id: uuid, created: datetime):
        """
        Constructor for a Task instance.

        Params:
            task_id: UUID
                Unique ID to represent the task
            created: datetime
                Tha date and time of creation of the task
        """
        self.task_id = task_id
        self.created = created

    def __repr__(self):
        return f"{self.__class__.__name__} ('{self.task_id}', '{self.created}')"
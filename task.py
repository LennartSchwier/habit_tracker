import uuid
import datetime


class Task:

    def __init__(self, task_id: uuid, created: datetime):
        self.task_id = task_id
        self.created = created

    def __repr__(self):
        return f"{self.__class__.__name__} ('{self.task_id}', '{self.created}')"
class HabitNameAlreadyExistsError(Exception):

    def __int__(self, message="A habit with that name already exists!"):
        self.message = message


class HabitNameIsUnknownError(Exception):

    def __init__(self, message="This habit name is unknown!"):
        self.message = message


class HabitSaveError(Exception):

    def __init__(self, message="Something went wrong trying to safe the habit!"):
        self.message = message


class HabitDeletionError(Exception):

    def __init__(self, message="Something went wrong trying to delete the habit!"):
        self.message = message

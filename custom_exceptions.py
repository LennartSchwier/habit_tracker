class UserNameAlreadyExistsError(Exception):

    def __init__(self, message="A user with that name already exists!"):
        self.message = message


class UserNameIsUnknownError(Exception):

    def __init__(self, message="This user is unknown!"):
        self.message = message


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


class MissingAuthorizationError(Exception):

    def __init__(self, message="Missing authorization!"):
        self.message = message


class UpdateActiveStatusError(Exception):

    def __init__(self, message="Something went wrong trying to update the status"):
        self.message = message

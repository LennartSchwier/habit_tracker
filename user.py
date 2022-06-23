"""Contains the User class"""


class User:
    """
    Class to represent a user.

    Attributes:
        user_name: str
            Unique user_name to represent the user
        password: str
           Password of the user
       is_admin: bool
            Indicates if user is registered as admin (default False)
    """

    def __init__(self, user_name: str, password: str, is_admin="False"):
        """
        Constructor for a Habit instance.

        Params:
        user_name: str
            Unique user_name to represent the user
        password: str
           Password of the user
       is_admin: bool
            Indicates if user is registered as admin (default False)
        """
        self.user_name = user_name
        self.password = password
        self.is_admin = is_admin

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"('{self.user_name}, {self.password}, {self.is_admin}')"

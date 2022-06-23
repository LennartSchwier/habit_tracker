"""
Contains the logic to access all database functionalities related to user management.

Functions:
    validate_password(db: str, user_name: str, password: str) -> bool
        Receives username and password and validates if it matches the database entries.
    get_user_by_name(db: str, user_name: str) -> User or None
        Asks the database for a user item and returns it as a User instance if found, otherwise None.
    add_user(db: str, user: User)
        Takes a User instance and adds it to the database.
    remove_user(db: str, active_user: str, user_name: str)
        Removes a user from the database.
    get_all_users(db: str)
        Returns a list of all stored users.
"""
from db import store_user_item, get_user_item_by_name, delete_user_item, get_all_user_items
from custom_exceptions import MissingAuthorizationError
from user import User


def validate_password(db: str, user_name: str, password: str) -> bool:
    """
    Receives username and password and validates if it matches the database entries.

    Params:
        db: str
            Name of the database in which the user is stored
        user_name: str
            Name of the user
        password: str
            SH3_256 hash of the entered password

    Return:
        bool
            True if the entered username/password combination matches the database entries, False otherwise.
    """
    user_item = get_user_item_by_name(db, user_name)
    if user_item:
        return user_item[0][2] == password
    else:
        return False


def get_user_by_name(db: str, user_name: str) -> User or None:
    """
    Asks the database for a user item and returns it as a User instance if found, otherwise None.

    Params:
        db: str
            Name of the database in which the user is stored
        user_name: str
            Name of the user

    Returns:
        User or None
            If user is found in database it is returned as a User instance, if not None is returned
    """
    user_item = get_user_item_by_name(db, user_name)
    if user_item is not None:
        return User(
            user_name=user_item[0][1],
            password=user_item[0][2],
            is_admin=user_item[0][3]
        )
    else:
        return None


def add_user(db: str, user: User):
    """
    Takes a User instance and adds it to the database.

    Params:
        db: str
            Name of the database in which the user is stored
        user: User
            The User instance that shall be stored in the database
    """
    store_user_item(db, user.user_name, user.password, user.is_admin)


def remove_user(db: str, active_user: str, user_name: str):
    """
    Removes a user from the database.

    Only an admin can remove users from the database. Therefore, proper authorization is checked before removal
    and an exception is raised if the logged-in user is not registered as admin.

    Params:
        db: str
            Name of the database in which the user is stored
        active_user: str
            Name of the currently logged-in user
        user_name: str
            Name of the user which shall be deleted

    Raise:
        MissingAuthorizationError
            Raised if a none admin user tries to delete a user
    """
    if get_user_by_name(db, active_user).is_admin == "True":
        delete_user_item(db, user_name)
    else:
        raise MissingAuthorizationError


def get_all_users(db: str):
    """
    Returns a list of all stored users.

    Param:
        db: str
            Name of the database in which the users are stored

    Return:
        all_user: list
            A list of all the users found in the database, can be empty.
    """
    all_users = []
    for item in get_all_user_items(db):
        user = User(item[1], item[2], item[3])
        all_users.append(user)
    return all_users

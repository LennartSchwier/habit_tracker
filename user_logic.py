from db import store_user_item, get_user_item_by_name, delete_user_item, get_all_user_items
from custom_exceptions import MissingAuthorizationError, UserNameIsUnknownError
from user import User


def validate_password(db, user_name: str, password: str):
    user_item = get_user_item_by_name(db, user_name)
    if user_item:
        if user_item[0][2] == password:
            return True
        else:
            return False
    else:
        raise UserNameIsUnknownError

def get_user_by_name(db, user_name: str):
    user_item = get_user_item_by_name(db, user_name)
    if user_item is not None:
        return User(
            user_name=user_item[0][1],
            password=user_item[0][2],
            is_admin=user_item[0][3]
        )
    else:
        return None


def add_user(db, user: User):
    store_user_item(db, user.user_name, user.password, user.is_admin)


def remove_user(db, active_user, user_name):
    if get_user_by_name(db, active_user).is_admin == "True":
        delete_user_item(db, user_name)
    else:
        raise MissingAuthorizationError


def get_all_users(db):
    all_users = []
    for item in get_all_user_items(db):
        user = User(item[1], item[2], item[3])
        all_users.append(user)
    return all_users

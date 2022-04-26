class User:

    def __init__(self, user_name: str, password: str, is_admin=False):
        self.user_name: user_name
        self.password: password
        self.is_admin: is_admin
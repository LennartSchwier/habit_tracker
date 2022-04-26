class User:

    def __init__(self, user_name: str, password: str, is_admin=False):
        self.user_name =user_name
        self.password = password
        self.is_admin = is_admin

    def __repr__(self):
        return f"{self.__class__.__name__}" \
               f"('{self.user_name}, {self.password}, {self.is_admin}')"
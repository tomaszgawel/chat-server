class UserStore:

    def __init__(self):
        self.online_users = []

    def add_new_user(self, user_name: str):
        self.online_users.append(user_name)

    def remove_user(self, user_name: str):
        if user_name in self.online_users:
            self.online_users.remove(user_name)

    def check_if_online(self, user_name: str) -> bool:
        return user_name in self.online_users

    pass

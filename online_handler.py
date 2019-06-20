class UserStore:

    def __init__(self):
        self.user_writer_map = {}

    def add_new_user(self, user_name, socket=None):
        self.user_writer_map[user_name] = socket

    def remove_user(self, user_name):
        if user_name in self.user_writer_map.keys():
            del self.user_writer_map[user_name]

    def check_if_online(self, user_name):
        return user_name in self.user_writer_map.keys()

    def remove_by_writer(self, writer):
        for user_name, wr in self.user_writer_map.values():
            if wr == writer:
                del self.user_writer_map[user_name]

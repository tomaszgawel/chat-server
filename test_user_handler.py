import unittest

from online_handler import UserStore


class TestStore(unittest.TestCase):
    store = UserStore()

    def test_add_user(self):
        self.store.add_new_user("test1")
        self.assertEqual(len(self.store.user_writer_map), 1)

    def test_remove_user(self):
        self.store.remove_user("test1")
        self.assertFalse("test1" in self.store.user_writer_map)

    def test_check_if_user_online_after_add(self):
        self.store.add_new_user("test3")
        self.assertTrue(self.store.check_if_online("test3"))

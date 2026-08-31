from unittest import TestCase

import coupang_functions as cf


class Test(TestCase):
    def test_get_items(self):
        session = cf.get_profile()
        cf.get_items("사과", session)

    def test_get_profile(self):
        session = cf.get_profile()

import unittest
import os
from datetime import datetime
from lib.reminder.recommend import Recommend


class TestRecommend(unittest.TestCase):

    def setUp(self):
        self.target = Recommend()

    def test_recommend_amazon_new_book(self):
        assert self.target.recommend_amazon_new_book(target_release_day='2020/2/22') is not None


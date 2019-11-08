import unittest
from lib.bookbot.entry import Entry
from lib import app_home


class TestEntry(unittest.TestCase):

    def setUp(self):
        self.entry = Entry()

    def test_make_approved_pdf(self):
        item = {
            'entry_no': '20191103020628891',
            'book_name': 'ゼロから作るDeep Learning ―Pythonで学ぶディープラーニングの理論と実装',
            'book_type': '本',
            'book_price': '3740',
            'book_url': 'https://www.amazon.co.jp//dp/4873117585/',
            'entry_time': '20191103020628',
            'slack_id': 'UC5KXFWJK',
            'slack_name': 'hoshino.tetsuya',
            'real_name': '星野 徹也',
            'permalink': 'https://niftycorp.slack.com/archives/CC6DENSDV/p1572714388012800'
        }
        save_path = self.entry.make_approved_pdf(item, f'{app_home}/file/test.pdf')
        assert save_path == f'{app_home}/file/test.pdf'

    def test_get_channel_name(self):
        channel_name = self.entry.get_channel_name('CC6DENSDV')
        assert channel_name == 'test_hoshino'

    def test_check_money_limit_per_user(self):
        slack_name = 'hoshino.tetsuya'
        book_price = '5000'
        self.assertFalse(self.entry.check_money_limit_per_user(slack_name, book_price))
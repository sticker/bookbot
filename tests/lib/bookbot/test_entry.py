import pytest
from lib.bookbot.entry import Entry


def test_make_approved_html():
    item = {
        'entry_no': '20191103020628891',
        'book_name': 'ゼロから作るDeep Learning ―Pythonで学ぶディープラーニングの理論と実装',
        'book_type': '本',
        'book_price': '3740',
        'book_url': 'https://www.amazon.co.jp//dp/4873117585/',
        'entry_time': '20191103020628',
        'slack_id': 'UC5KXFWJK',
        'slack_name': 'hoshino.tetsuya',
        'real_name': '星野 徹也'
    }
    save_path = Entry().make_approved_html(item)
    assert save_path == 'file/20191103020628891.html'


def test_get_channel_name():
    channel_name = Entry().get_channel_name('CC6DENSDV')
    assert channel_name == 'test_hoshino'

if __name__ == '__main__':
    print(test_make_approved_html())
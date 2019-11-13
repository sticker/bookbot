import pytest
from datetime import datetime
from lib.util.pdf import Pdf

target = Pdf()

item = dict()
item['entry_no'] = '10'
item['book_name'] = '機械学習エンジニアになりたい人のための本 AIを天職にする'
item['book_type'] = 'Kindle'
item['book_price'] = '2069'
item['total_price_in_this_year'] = 11129
item['remain_amount'] = 15940
item['book_url'] = 'https://www.amazon.co.jp/dp/B07GWM4J7H/'
item['purpose'] = '機械学習エンジニアになるため'
item['entry_time'] = '20191113123801'
item['slack_id'] = 'UC5KXFWJK'
item['slack_name'] = 'hoshino.tetsuya'
item['real_name'] = '星野　徹也'
item['permalink'] = 'https://niftycorp.slack.com/archives/CC6DENSDV/p1573616280097900'
item['impression'] = ''

def test_make_approved_html():

    html = target.make_approved_html(item)
    print(html)
    assert "Kindle" in html

def test_make_approved_pdf():
    target.make_approved_pdf(item, 'test.pdf')
import pytest
from datetime import datetime
from lib.util.converter import Converter

target = Converter()


def test_to_hankaku():
    assert target.to_hankaku('ＡＢＣＤＥ') == 'ABCDE'
    assert target.to_hankaku('　あいうえお　０１２３４５６７８９') == '　あいうえお　0123456789'


def test_get_this_year_from_today():
    assert target.get_this_year_from_today(datetime.strptime('2019-04-01', '%Y-%m-%d')) == ('20190401', '20190401')
    assert target.get_this_year_from_today(datetime.strptime('2019-03-31', '%Y-%m-%d')) == ('20180401', '20190331')
    assert target.get_this_year_from_today(datetime.strptime('2019-05-01', '%Y-%m-%d')) == ('20190401', '20190501')
    assert target.get_this_year_from_today(datetime.strptime('2019-01-01', '%Y-%m-%d')) == ('20180401', '20190101')
    assert target.get_this_year_from_today(datetime.strptime('2020-02-29', '%Y-%m-%d')) == ('20190401', '20200229')


def test_get_date_str():
    assert target.get_date_str('20200320') == '2020-03-20'


def test_get_book_type_str():
    assert target.get_book_type_str('本') == ''
    assert target.get_book_type_str('Kindle') == '(Kindle)'
    assert target.get_book_type_str('test') == '(test)'


def test_get_list_str():
    item = dict()
    item['entry_no'] = '1'
    item['book_url'] = 'http://test.com'
    item['book_name'] = '購入した書籍のタイトル'
    item['book_type'] = '本'
    item['entry_time'] = '20190401233626'
    item['real_name'] = 'テスト　太郎'
    item['impression'] = 'おもしろかったです'
    assert target.get_list_str(item) == "[1] <http://test.com|購入した書籍のタイトル> at 2019-04-01 by テスト　太郎:memo:"
    item['impression'] = ''
    assert target.get_list_str(item) == "[1] <http://test.com|購入した書籍のタイトル> at 2019-04-01 by テスト　太郎"

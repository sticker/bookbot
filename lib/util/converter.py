from datetime import datetime, timedelta


class Converter:
    def __init__(self):
        pass

    def to_hankaku(self, text: str):
        return text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

    def get_this_year_from_today(self, today=datetime.today()):
        today_md = today.strftime('%m%d')
        if int(today_md) < int('0401'):
            start = today.replace(year=today.year -1, month=4, day=1)
        else:
            start = today.replace(month=4, day=1)

        end = today

        return start.strftime('%Y%m%d'), end.strftime('%Y%m%d')

    def get_target_year_start_end(self, target_yyyy: str):
        target_year = datetime.strptime(target_yyyy, '%Y')
        start = target_year.replace(month=4, day=1)
        end = target_year.replace(year=target_year.year +1, month=3, day=31)

        return start.strftime('%Y%m%d'), end.strftime('%Y%m%d')

    def get_date_str(self, yyyymmdd):
        date_str = f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
        return date_str

    def get_book_type_str(self, book_type):
        book_type_str = ''
        if book_type != '本':
            book_type_str = f'({book_type})'
        return book_type_str

    def get_list_str(self, item):
        entry_no = item.get('entry_no', '-')
        book_url = item.get('book_url', '-')
        book_name = item.get('book_name', '-')
        book_type = self.get_book_type_str(item.get('book_type', '本'))
        entry_date_yyyymmdd = item.get('entry_time', '99999999')[0:8]
        entry_date = self.get_date_str(entry_date_yyyymmdd)
        real_name = item.get('real_name', '-')
        impression = item.get('impression', '')
        has_impression = ''
        if impression != '':
            has_impression = ":memo:"

        return f"*[{entry_no}]* <{book_url}|{book_name}>{book_type} at {entry_date} by {real_name}{has_impression}"

    def get_yyyymmdd_specified_days_ago(self, days_ago: int, today=datetime.today()):
        specified_days_ago = today - timedelta(days_ago)
        return specified_days_ago.strftime('%Y%m%d')

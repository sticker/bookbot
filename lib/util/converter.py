from datetime import datetime


class Converter:
    def __init__(self):
        pass

    def to_hankaku(self, text: str):
        return text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))

    def get_this_year_from_today(self):
        today = datetime.today()
        today_md = today.strftime('%m%d')
        if int(today_md) <= int('0420'):
            start = today.replace(year=today.year -1, month=4, day=21)
            end = today.replace(month=4, day=20)
        else:
            start = today.replace(month=4, day=21)
            end = today

        return start.strftime('%Y%m%d'), end.strftime('%Y%m%d')

    def get_date_str(self, yyyymmdd):
        date_str = f"{yyyymmdd[0:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
        return date_str

    def get_book_type_str(self, book_type):
        book_type_str = ''
        if book_type != '本':
            book_type_str = f'({book_type})'
        return book_type_str

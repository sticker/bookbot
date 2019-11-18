from slackbot.dispatcher import Message


class Validation:
    def __init__(self):
        pass

    def validate_entry(self, **kwargs):
        check_ok = True
        # 各パラメータのバリデーションを呼び出す
        if not self.__validate_book_name(kwargs['book_name'], kwargs['message']):
            check_ok = False
        if not self.__validate_book_price(kwargs['book_price'], kwargs['message']):
            check_ok = False
        if not self.__validate_book_url(kwargs['book_url'], kwargs['message']):
            check_ok = False

        return check_ok

    def __validate_book_name(self, book_name: str, message: Message) -> bool:
        """
        書籍名のバリデーション
        :param book_name: 書籍名
        :return:
        """
        # 何チェックする？
        return True

    def __validate_book_price(self, book_price: str, message: Message) -> bool:
        """
        立替金額のバリデーション
        :param book_price: 立替金額
        :return:
        """
        if not book_price.isdecimal():
            message.send("立替金額は数字で入力してください", thread_ts=message.body['ts'])
            return False

        return True

    def __validate_book_url(self, book_url: str, message: Message) -> bool:
        """
        詳細URLのバリデーション
        :param book_url: 詳細URL
        :param message:
        :return:
        """
        return True

    def validate_impression(self, **kwargs):
        check_ok = True
        # 各パラメータのバリデーションを呼び出す
        if not self.__validate_entry_no(kwargs['entry_no'], kwargs['message']):
            check_ok = False

        return check_ok

    def __validate_entry_no(self, entry_no: str, message: Message) -> bool:
        if not entry_no.isdecimal():
            message.send("登録番号は数字で入力してください", thread_ts=message.body['ts'])
            return False

        return True

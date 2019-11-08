from slackbot.bot import listen_to
from slackbot.bot import respond_to
from slackbot.dispatcher import Message
from lib.bookbot.entry import Entry
from lib.bookbot.impression import Impression
from lib.bookbot.list_history import ListHistory
from lib.bookbot.describe import Describe

import logging
logging.basicConfig(level=logging.DEBUG)

entry = Entry()
impression = Impression()
list_history = ListHistory()
describe = Describe()

@respond_to('help')
@listen_to('Can someone help me?')
def help(message: Message):
    """
    ヘルプメッセージを表示する
    :param message:
    :return:
    """
    usage = "`@bookbot help` : このメッセージを表示する\n"
    message.reply(usage)


@listen_to('送信しました')
def workflow_handler(message: Message):
    logging.info(message.body)

    username = message.body['username']

    # ワークフロー：書籍購入 からのメッセージに反応する
    if username == '書籍購入':
        entry.save(message)
    # ワークフロー：感想登録 からのメッセージに反応する
    elif username == '書籍購入後の感想登録':
        impression.save(message)
    else:
        logging.debug("ワークフローからのメッセージでないため無視します")

    return


@respond_to('list\s*(.*)')
def list_handler(message: Message, option):
    logging.info(message.body)
    logging.info(option)
    logging.info(option.strip())

    list_history.default(message)


@respond_to('desc\s*(\d*)')
def list_handler(message: Message, entry_no):
    logging.info(message.body)

    describe.specified_entry_no(message, entry_no)
from slackbot.bot import listen_to
from slackbot.bot import respond_to
from slackbot.dispatcher import Message
from lib.bookbot.entry import Entry
from lib.bookbot.list_history import ListHistory

import logging
logging.basicConfig(level=logging.DEBUG)

entry = Entry()
list_history = ListHistory()

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
    logging.info(message)

    # ワークフロー：書籍購入 からのメッセージに反応する
    if message.body['username'] == '書籍購入':
        entry.save(message)
    else:
        logging.debug("Botからのメッセージでないため無視します")

    return


@respond_to('list')
def list_handler(message):
    list_history.default(message)

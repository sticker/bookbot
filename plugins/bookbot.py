from slackbot.bot import listen_to
from slackbot.bot import respond_to
from slackbot.dispatcher import Message
from lib.bookbot.entry import Entry
from lib.bookbot.impression import Impression
from lib.bookbot.list_history import ListHistory
from lib.bookbot.describe import Describe
from lib.bookbot.delete import Delete
from lib.util.slack import Slack

import os
import logging
logging.basicConfig(level=logging.DEBUG)

entry = Entry()
impression = Impression()
list_history = ListHistory()
describe = Describe()
delete = Delete()
slack = Slack()

default_channel_id = os.getenv('DEFAULT_CHANNEL_ID', 'CC6DENSDV')

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
def list_handler(message: Message, search_words_str):
    logging.info(message.body)
    search_words = search_words_str.strip().replace("　", " ").split()
    logging.info(search_words)

    if len(search_words) == 0 or len(search_words) == 1 and search_words[0] == '':
        list_history.default(message)
    else:
        list_history.search(message, search_words)


@respond_to('(desc|describe|display|詳細)\s*(\d*)')
def list_handler(message: Message, commmand, entry_no):
    logging.info(message.body)

    describe.specified_entry_no(message, entry_no)


@respond_to('(delete|del|rm|削除)\s*(\d*)')
def delete_handler(message: Message, command, entry_no):
    logging.info(message.body)

    if message.body['channel'] != default_channel_id:
        message.send(f"公式チャンネル #{slack.get_channel_name(message, channel_id=default_channel_id)} で実行してください！")
        return

    delete.specified_entry_no(message, entry_no)


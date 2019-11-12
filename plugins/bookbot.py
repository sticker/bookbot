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
def help(message: Message):
    """
    ヘルプメッセージを表示する
    :param message:
    :return:
    """
    botname = "bookbot"
    usages = list()
    usages.append(f"`{botname} list` : 過去1年間の登録情報をリスト表示する")
    usages.append(f"`{botname} list [検索文字]` : 題名・氏名・Slack名 で絞り込む（複数指定でAND検索）")
    usages.append(f"`{botname} desc [登録番号]` : 指定した番号の登録情報を感想付きで表示する")
    usages.append(f"`{botname} rm [登録番号]` : 指定した番号の登録情報を削除する")
    message.reply("\n".join(usages))


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
def describe_handler(message: Message, commmand, entry_no):
    logging.info(message.body)

    describe.specified_entry_no(message, entry_no)


@respond_to('(delete|del|rm|削除)\s*(\d*)')
def delete_handler(message: Message, command, entry_no):
    logging.info(message.body)

    if message.body['channel'] != default_channel_id:
        text = f"公式チャンネル #{slack.get_channel_name(message, channel_id=default_channel_id)} で実行してください！"
        slack.send_message_with_link_names(message, message.body['channel'], text)
        return

    delete.specified_entry_no(message, entry_no)


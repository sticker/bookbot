from slackbot import settings
from slackbot.bot import listen_to
from slackbot.bot import respond_to
from slackbot.dispatcher import Message
from lib.bookbot.help import Help
from lib.bookbot.entry import Entry
from lib.bookbot.impression import Impression
from lib.bookbot.list_history import ListHistory
from lib.bookbot.describe import Describe
from lib.bookbot.total import Total
from lib.bookbot.delete import Delete
from lib.util.slack import Slack
import logging


@respond_to('help')
def help(message: Message):
    logging.info(message.body)

    Help().default(message)


@listen_to('送信しました')
def workflow_handler(message: Message):
    logging.info(message.body)

    username = message.body['username']

    # ワークフロー：書籍購入 からのメッセージに反応する
    if username == '書籍購入' or username == '書籍購入-test':
        Entry().save(message)
    # ワークフロー：感想登録 からのメッセージに反応する
    elif username == '書籍購入後の感想登録' or username == '書籍購入後の感想登録-test':
        Impression().save(message)
    else:
        logging.debug("ワークフローからのメッセージでないため無視します")

    return


@respond_to('list\s*(.*)')
def list_handler(message: Message, search_words_str):
    logging.info(message.body)
    search_words = search_words_str.strip().replace("　", " ").split()
    logging.info(search_words)

    if len(search_words) == 0 or len(search_words) == 1 and search_words[0] == '':
        ListHistory().default(message)
    else:
        ListHistory().search(message, search_words)


@respond_to('(desc|describe|display|detail|詳細)\s*(\d*)')
def describe_handler(message: Message, command, entry_no):
    logging.info(message.body)

    if entry_no is None or entry_no == '':
        message.send(f"{command} のあとに登録番号（半角数字のみ）を入力してください")
        return

    Describe().specified_entry_no(message, entry_no)


@respond_to('(delete|del|rm|削除)\s*(\d*)')
def delete_handler(message: Message, command, entry_no):
    logging.info(message.body)

    if message.body['channel'] != settings.DEFAULT_CHANNEL_ID:
        slack = Slack()
        text = f"公式チャンネル #{slack.get_channel_name(message, channel_id=settings.DEFAULT_CHANNEL_ID)} で実行してください！"
        slack.send_message_with_link_names(message, message.body['channel'], text)
        return

    if entry_no is None or entry_no == '':
        message.send(f"{command} のあとに登録番号（半角数字のみ）を入力してください")
        return

    Delete().specified_entry_no(message, entry_no)

@respond_to('(total|合計)\s*(\S*)\s*(\d*)')
def total_handler(message: Message, command, option, target_yyyy):
    logging.info(message.body)
    logging.info(f"command={command}")
    logging.info(f"option={option}")
    logging.info(f"target_yyyy={target_yyyy}")
    if 'all' in option or '全て' in option:
        Total().all_total_price_in_year(message, target_yyyy)
    else:
        Total().default(message)

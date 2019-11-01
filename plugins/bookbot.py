from slackbot.bot import listen_to
from slackbot.bot import respond_to
from lib.aws.dynamodb import Dynamodb
from datetime import datetime
import logging
logging.basicConfig(level=logging.DEBUG)

dynamodb = Dynamodb()


@respond_to('help')
@listen_to('Can someone help me?')
def help(message):
    """
    ヘルプメッセージを表示する
    :param message:
    :return:
    """
    usage = "`@bookbot help` : このメッセージを表示する\n"
    logging.warning(f"usage={usage}")
    logging.info(f"usage={usage}")
    message.reply(usage)


@listen_to('送信しました')
def workflowtest(message):
    logging.info(message._body)

    # Botからのメッセージでなければ反応しない
    if message.body['username'] != '書籍購入申請':
        logging.debug("Botからのメッセージでないため無視します")
        return

    book_name = ''
    book_price = ''
    book_url = ''
    for block in message.body['blocks']:
        if not ('text' in block and 'text' in block['text']):
            continue

        text = block['text']['text']
        if '*書籍名*' in text:
            book_name = text.replace('*書籍名*', '').replace('\n', '')
        elif '*金額*' in text:
            book_price = text.replace('*金額*', '').replace('\n', '')
        elif '*詳細リンク（Amazonなど）*' in text:
            book_url = text.replace('*詳細リンク（Amazonなど）*', '').replace('\n', '')

    # TODO: パラメータチェック

    # 受付番号
    entry_no = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    logging.info(f"entry_no={entry_no}")

    item = {
        'entry_no': entry_no,
        'book_name': book_name,
        'book_price': book_price,
        'book_url': book_url
    }

    dynamodb.insert('bookbot-entry', item)

    message.send(f"申請を受け付けました！ book_name={book_name}, book_price={book_price}, book_url={book_url}")

import logging
import schedule
import threading
import time
from slackbot.bot import Bot

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) {%(filename)s:%(lineno)d} %(message)s',
                    )


def main():
    bot = Bot()
    bot.run()


def remind_impression():
    logging.info("remind!")


def remind_impression_minutes():
    logging.info("remind minutes!")


def reminder():
    schedule.every().day.at("23:49").do(remind_impression)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print('start reminder')
    remind_thread = threading.Thread(target=reminder)
    remind_thread.start()
    print('start slackbot')
    main()


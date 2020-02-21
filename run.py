import logging
import schedule
import threading
import time
from slackbot import settings
from slackbot.bot import Bot
from lib.reminder.reminder import Reminder
from lib.reminder.recommend import Recommend

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) {%(filename)s:%(lineno)d} %(message)s',
                    )

reminder = Reminder()
recommend = Recommend()


def main():
    bot = Bot()
    bot.run()


def scheduler():
    reminder_time = settings.IMPRESSION_REMINDER_TIME
    schedule.every().day.at(reminder_time).do(reminder.remind_impression)

    recommend_time = settings.NEW_BOOK_RECOMMEND_TIME
    schedule.every().day.at(recommend_time).do(recommend.recommend_amazon_new_book)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print('start reminder')
    schedule_thread = threading.Thread(target=scheduler)
    schedule_thread.start()

    print('start slackbot')
    main()


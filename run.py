import logging
import schedule
import threading
import time
from slackbot import settings
from slackbot.bot import Bot
from lib.reminder.reminder import Reminder

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) {%(filename)s:%(lineno)d} %(message)s',
                    )

reminder = Reminder()


def main():
    bot = Bot()
    bot.run()


def reminder_schedule():
    reminder_time = settings.IMPRESSION_REMINDER_TIME
    schedule.every().day.at(reminder_time).do(reminder.remind_impression)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print('start reminder')
    remind_thread = threading.Thread(target=reminder_schedule)
    remind_thread.start()

    print('start slackbot')
    main()


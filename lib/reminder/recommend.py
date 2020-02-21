from slackbot import settings
from lib import get_logger
from lib.util.slack import Slack
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


class Recommend:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.slack = Slack()

    def recommend_amazon_new_book(self, target_release_day=datetime.today().strftime('%Y/%-m/%-d')):
        self.logger.debug(target_release_day)

        self.logger.info(f"Amazonの新刊ランキングから今日発売の本をリコメンドします")

        target_url = 'https://www.amazon.co.jp/gp/new-releases/books/466298/'
        r = requests.get(target_url)
        soup = BeautifulSoup(r.text, 'lxml')

        text_list = list()
        for item in soup.find_all('li', class_="zg-item-immersion"):
            title = item.img['alt']
            href = item.a['href']
            url = 'https://www.amazon.co.jp' + href
            # kind = item.find_all('div', class_="a-row")[2].span.string
            price = item.find('span', class_="p13n-sc-price").string
            release = item.div.find('span', class_="zg-release-date").string
            release_yyyymmdd = re.match(r'.*?(\d+/\d+/\d+).*', release).group(1)
            self.logger.debug(release_yyyymmdd)
            # self.logger.debug(f"{title} {url} {price} {release}")

            if release_yyyymmdd == target_release_day:
                text_list.append(f"<{url}|{title}> `{price}`")

        self.logger.debug("\n".join(text_list))
        if len(text_list) > 0:
            channel_name = self.slack.get_channel_name_by_slacker(settings.DEFAULT_CHANNEL_ID)
            text_list.insert(0, f"{target_release_day} 発売の新刊がありますよ！")
            self.slack.send_message_by_slacker(channel=channel_name, text="\n".join(text_list))

        return True

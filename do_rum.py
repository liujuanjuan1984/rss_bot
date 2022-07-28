import datetime
import time

from blaze.config import DB_NAME as blaze_db_name
from blaze.config import MIXIN_KEYSTORE
from rss import RumBot
from rss.config import DB_NAME as rss_db_name
from rss.config import RUM_PORT, SEEDURL

bot = RumBot(blaze_db_name, rss_db_name, MIXIN_KEYSTORE, RUM_PORT, SEEDURL)
while True:
    print(datetime.datetime.now(), "do_rss...")
    bot.do_rss()  # Rum 动态转发到 xin
    print(datetime.datetime.now(), "send_to_rum...")
    bot.send_to_rum()  # 帮 xin 用户代发内容到 Rum
    time.sleep(0.1)

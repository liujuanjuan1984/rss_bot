import time

from blaze.config import DB_NAME as blaze_db_name
from blaze.config import MIXIN_KEYSTORE
from rss import RumBot
from rss.config import DB_NAME as rss_db_name

# (self, blaze_db_name, rss_db_name, mixin_keystore, rum_port):
bot = RumBot(blaze_db_name, rss_db_name, MIXIN_KEYSTORE, 51098)
while True:
    try:
        bot.do_rss()
    except Exception as e:
        print(e)
    time.sleep(0.1)

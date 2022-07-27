import datetime
import time

from blaze.config import DB_NAME as blaze_db_name
from blaze.config import MIXIN_KEYSTORE
from rss import RumBot
from rss.config import DB_NAME as rss_db_name

bot = RumBot(blaze_db_name, rss_db_name, MIXIN_KEYSTORE, 51098)

today = datetime.date.today()
bot.airdrop_to_bot(memo=f"{today} Rum 订阅器空投")

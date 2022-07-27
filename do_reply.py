from blaze.config import DB_NAME as blaze_db_name
from blaze.config import MIXIN_KEYSTORE
from rss import ReplyBot
from rss.config import DB_NAME as rss_db_name

"""
回复用户消息
并根据指令更新用户订阅信息
"""
bot = ReplyBot(blaze_db_name, rss_db_name, MIXIN_KEYSTORE)
bot.reply_forever()

import datetime
import time

from rss import ReplyBot

"""
回复用户消息
并根据指令更新用户订阅信息
"""
bot = ReplyBot()

while True:
    try:
        bot.reply()
    except Exception as e:
        print(datetime.datetime.now(), "reply failed:", e)
        bot = ReplyBot()

    time.sleep(1)

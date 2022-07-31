import time

from rss import ReplyBot

"""
回复用户消息
并根据指令更新用户订阅信息
"""
bot = ReplyBot()

while True:
    bot.reply()
    time.sleep(1)

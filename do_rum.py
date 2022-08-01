import datetime
import time

from rss import RumBot

bot = RumBot()
while True:
    try:
        bot.do_rss()  # Rum 动态转发到 xin
    except Exception as e:
        print(datetime.datetime.now(), "do_rss failed:", e)
        bot = RumBot()
    time.sleep(1)

    try:
        bot.send_to_rum()  # 帮 xin 用户代发内容到 Rum
    except Exception as e:
        print(datetime.datetime.now(), "send_to_rum failed", e)
        bot = RumBot()
    time.sleep(1)

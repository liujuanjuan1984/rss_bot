import datetime
import time

from rss import RumBot

bot = RumBot()
while True:
    bot.do_rss()  # Rum 动态转发到 xin
    bot.send_to_rum()  # 帮 xin 用户代发内容到 Rum
    time.sleep(1)

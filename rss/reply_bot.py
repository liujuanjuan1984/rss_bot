import datetime
import logging
import re
import time

from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data

from blaze.config import DB_NAME as BLAZE_DB_NAME
from blaze.config import HTTP_ZEROMESH, MIXIN_KEYSTORE
from blaze.models import BlazeDB
from rss.config import DB_NAME as RSS_DB_NAME
from rss.config import *
from rss.models import RssDB
from rss.seven_years_circle import SevenYearsCircle

logger = logging.getLogger(__name__)


class ReplyBot:
    def __init__(self, blaze_db_name=BLAZE_DB_NAME, rss_db_name=RSS_DB_NAME, mixin_keystore=MIXIN_KEYSTORE):
        self.config = AppConfig.from_payload(mixin_keystore)
        self.blaze_db = BlazeDB(blaze_db_name, echo=False, reset=False)
        self.rss_db = RssDB(rss_db_name, echo=False, reset=False)
        self.xin = HttpClient_AppAuth(self.config, api_base=HTTP_ZEROMESH)

    def get_reply_text(self, text):
        if type(text) == str and text.lower() in ["hi", "hello", "你好", "订阅"]:
            return WELCOME_TEXT, None

        if type(text) == str and text.startswith("代发"):
            if len(text) < 5:  # too short to send
                return "太短啦", None
            return "收到，将为您自动发送到去中心微博", None

        if type(text) == str and text.startswith("生日"):
            reply_text = (
                "请按如下格式输入，以“生日”开头，“年月日”的数字之间要用空格或其它标点符号分开。以下写法都是支持的：\n生日 1990 1 24\n生日，2001。12。24\n生日1972 7 12\n"
            )
            rlts = re.findall(r"^生日\D*?(\d{4})\D*?(\d{1,2})\D*?(\d{1,2})\D*?$", text)
            if rlts:
                try:
                    reply_text = SevenYearsCircle(*rlts[0]).text_status()
                except:
                    pass
            return reply_text, None

        try:
            _num = int(text)
            _abs = abs(_num)
        except:
            return "输入 hi 查看操作说明", None

        if str(_abs) not in list(RSS_BOT_COMMANDS.keys()):
            return "输入 hi 查看操作说明", None

        irss = {}  # init
        for group_id in RSS_GROUPS:
            irss[group_id] = None

        _gidx = RSS_BOT_COMMANDS[str(_abs)]["group_id"]
        if _gidx == None:  # 取消所有
            for _gid in irss:
                irss[_gid] = False
            reply_text = f"👌 Ok，您已取消订阅所有种子网络。{ADDS_TEXT}"
        elif _gidx == -1:  # 订阅所有
            for _gid in irss:
                irss[_gid] = True
            reply_text = f"✅ Yes，您已成功订阅所有种子网络。{ADDS_TEXT}"
        else:
            # 修改订阅：增加或推定
            _gname = RSS_BOT_COMMANDS[str(_abs)]["text"]
            if _num > 0:
                irss[_gidx] = True
                reply_text = f"✅ Yes，您已成功{_gname}{ADDS_TEXT}"
            else:
                # 取消订阅
                irss[_gidx] = False
                reply_text = f"👌 Ok，您已取消{_gname}{ADDS_TEXT}"
        return reply_text, irss

    def update_rss_for_user(self, user_id, irss):
        if irss is None:
            return
        for group_id in irss:
            if irss[group_id] is None:  # 没有更新订阅信息
                continue
            self.rss_db.update_rss(user_id, group_id, irss[group_id])

    def _reply(self, msg):

        reply_text, irss = self.get_reply_text(msg.text)
        self.update_rss_for_user(msg.user_id, irss)

        # send reply
        reply_msg = pack_message(
            pack_text_data(reply_text),
            conversation_id=self.xin.get_conversation_id_with_user(msg.user_id),
            quote_message_id=msg.message_id,
        )

        resp = self.xin.api.send_messages(reply_msg)

        if "data" in resp:
            self.blaze_db.set_message_replied(msg.message_id)
            print(f"{datetime.datetime.now()} {msg.message_id} replied")
            return True
        else:
            print(f"{datetime.datetime.now()} {msg.message_id} failed")
            return False

    def reply(self):
        msgs = self.blaze_db.get_messages_to_reply()
        for msg in msgs:
            try:
                r = self._reply(msg)
                print(datetime.datetime.now(), r, msg.message_id)
            except Exception as e:
                print(datetime.datetime.now(), f"{msg.message_id} failed: {e}")
                logger.error(f"{msg.message_id} failed: {e}")
            time.sleep(0.5)

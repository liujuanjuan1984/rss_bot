import datetime
import json
import logging
import os
import random
import re
import sys
import time

import rumpy
import rumpy.utils as utils
from mixinsdk.clients.http_client import HttpClient_AppAuth
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView, pack_message, pack_text_data
from rumpy import FullNode, HttpRequest
from sqlalchemy import Boolean, Column, Integer, String, and_, distinct

from blaze.config import DB_NAME, MIXIN_KEYSTORE
from blaze.modules import BlazeDB
from rss.config import *
from rss.modules import AirDrop, KeyStore, Profile, Rss, RssDB, Trx, TrxProgress, TrxStatus
from rss.seven_years_circle import SevenYearsCircle

logger = logging.getLogger(__name__)


class RumBot:
    def __init__(self, blaze_db_name, rss_db_name, mixin_keystore, rum_port):
        self.config = AppConfig.from_payload(mixin_keystore)
        self.blaze_db = BlazeDB(blaze_db_name, echo=False, reset=False)
        self.rss_db = RssDB(rss_db_name, echo=False, reset=False)
        self.xin = HttpClient_AppAuth(self.config)
        self.full_rum = FullNode(port=rum_port)
        self.groups = RSS_GROUPS
        self.update_all_profiles("bot")

    def update_profiles(self, group_id):
        _x = and_(
            TrxProgress.group_id == group_id,
            TrxProgress.progress_type == "GET_PROFILES",
        )
        progress = self.rss_db.session.query(TrxProgress).filter(_x).first()

        if progress == None:
            _p = {
                "progress_type": "GET_PROFILES",
                "trx_id": None,
                "timestamp": None,
                "group_id": group_id,
            }
            self.rss_db.add(TrxProgress(_p))

        p_tid = None if progress == None else progress.trx_id

        users_data = self.full_rum.api.update_profiles_data(
            group_id=group_id,
            users_data={"trx_id": p_tid},
            types=("name", "wallet"),
        )
        if users_data is None:
            return
        tid = users_data.get("trx_id")
        ts = users_data.get("trx_timestamp")

        if tid and tid != p_tid:
            self.rss_db.session.query(TrxProgress).filter(_x).update({"trx_id": tid, "timestamp": ts})
            self.rss_db.session.commit()

        users = users_data.get("data", {})
        for pubkey in users:
            if pubkey == "progress_tid":
                continue
            _name = users[pubkey].get("name", pubkey)
            _wallet = users[pubkey].get("wallet", None)
            if type(_wallet) == list:
                _wallet = _wallet[0]["id"]
            _x = and_(
                Profile.group_id == group_id,
                Profile.pubkey == pubkey,
            )
            existd = self.rss_db.session.query(Profile).filter(_x).first()
            if not existd:
                _p = {
                    "group_id": group_id,
                    "pubkey": pubkey,
                    "name": _name,
                    "wallet": _wallet,
                    "timestamp": ts,
                }
                self.rss_db.add(Profile(_p))
            elif existd.timestamp < ts:
                _p = {"timestamp": ts}
                if _name != existd.name:
                    _p["name"] = _name
                if _wallet != existd.wallet:
                    _p["wallet"] = _wallet

                self.rss_db.session.query(Profile).filter(_x).update(_p)
                self.rss_db.commit()

    def update_all_profiles(self, where="bot"):
        groups = []
        if where == "bot":
            groups = self.groups
        elif where == "node":
            groups = self.full_rum.api.groups_id

        for group_id in groups:
            self.update_profiles(group_id)

    def get_nicknames(self, group_id):
        _nn = self.rss_db.session.query(Profile).filter(Profile.group_id == group_id).all()
        nicknames = {}
        for _n in _nn:
            nicknames[_n.pubkey] = {"name": _n.name}
        return nicknames

    def get_group_trxs(self, group_id):
        if not self.full_rum.api.is_joined(group_id):
            logger.warning(f"group_id: {group_id}, you are not in this group. you need to join it.")
            return

        nicknames = self.get_nicknames(group_id)  # TODO:to update and check
        gname = self.groups[group_id]["group_name"]
        minutes = self.groups[group_id]["minutes"]

        # 获取 group trx 的更新进度
        existd = self.rss_db.get_trx_progress(group_id, "GET_CONTENT")
        if existd:
            trx_id = existd.trx_id
        else:
            _trxs = self.full_rum.api.get_group_content(group_id=group_id, reverse=True, num=10)
            if len(_trxs) > 0:
                trx_id = _trxs[-1]["TrxId"]
                _ts = str(utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]))
            else:
                trx_id = None
                _ts = None

            self.rss_db.add_trx_progress(group_id, trx_id, _ts, "GET_CONTENT")

        trxs = self.full_rum.api.get_group_content(group_id=group_id, trx_id=trx_id, num=10)
        for trx in trxs:
            # update get group content progress
            _tid = trx["TrxId"]
            ts = str(utils.timestamp_to_datetime(trx["TimeStamp"]))
            self.rss_db.update_trx_progress(group_id, _tid, ts, "GET_CONTENT")
            # add new trx to db

            # 只发距今xx小时的更新，间隔时间由配置文件控制
            if ts <= str(datetime.datetime.now() + datetime.timedelta(minutes=minutes)):
                continue

            # 数据库已存储
            if self.rss_db.get_trx(_tid):
                continue

            obj = self.full_rum.api.trx_retweet_params(group_id=group_id, trx=trx)
            if not obj:
                continue

            pubkey = trx["Publisher"]
            if pubkey not in nicknames:
                username = pubkey[-8:]
            else:
                username = nicknames[pubkey]["name"] + f"({pubkey[-8:]})" or pubkey[-8:]

            obj["content"] = f"{username}@{gname}\n{obj['content']}"
            text = obj["content"].encode().decode("utf-8")
            self.rss_db.add_trx(group_id, _tid, ts, text)

    def _check_text(self, text):
        # subs = (" 点赞给 `"," 点踩给 `"," 修改了个人信息：","OBJECT_STATUS_DELETED")
        # is_pass = utils.check_sub_strs(text,*subs)
        # if is_pass and not is_except:
        #    return False

        sub = "Happyness(hDZVqRpg)@Huoju在Rum上说了啥"
        is_except = utils.check_sub_strs(text, sub)

        subs = (" 点赞给 `", " 点踩给 `")
        is_split = utils.check_sub_strs(text, *subs)
        if is_split and not is_except:
            text = text.split("所发布的内容：")[0] + "所发布的内容。"

        # 移除种子来源展示
        if is_except:
            text = text.split("origin: ")[0]

        _length = 200
        if len(text) > _length:
            text = text[:_length] + "...略..."
        return text

    def send_group_msg_to_xin(self, group_id):

        nice_ts = str(datetime.datetime.now() + datetime.timedelta(minutes=self.groups[group_id]["minutes"]))
        # 获取待发的 trxs
        trxs = self.rss_db.get_trxs_later(group_id, nice_ts)

        # 筛选出待发的人
        users = self.rss_db.get_users_by_rss(group_id, True)

        for trx in trxs:
            logger.debug(f"trxs, trx_id:{trx.trx_id}")

            sent_users = self.rss_db.get_users_by_trx_sent(group_id, trx.trx_id)
            _sent_users = [i[0] for i in sent_users]

            text = self._check_text(trx.text)

            # 特殊处理，某些不对所有人发放的动态，会对自己发放。
            if text == False:
                if MY_XIN_USER_ID in _sent_users:
                    continue
                cid = self.xin.get_conversation_id_with_user(MY_XIN_USER_ID)
                msg = pack_message(pack_text_data(trx.text), cid)
                resp = self.xin.api.send_messages(msg)

                if "data" in resp:
                    self.rss_db.add_trx_sent(group_id, trx.trx_id, MY_XIN_USER_ID)

            else:
                packed = pack_text_data(trx.text)
                for user_id, *others in users:
                    if user_id in _sent_users:
                        continue
                    cid = self.xin.get_conversation_id_with_user(user_id)
                    msg = pack_message(packed, cid)
                    resp = self.xin.api.send_messages(msg)

                    if "data" in resp:
                        self.rss_db.add_trx_sent(group_id, trx.trx_id, user_id)

    def send_to_rum(self):
        mixin_msgs = self.blaze_db.get_messages_query("代发%")
        for msg in mixin_msgs:
            if self.blaze_db.get_messages_status(msg.message_id, "SEND_TO_RUM"):
                continue

            pvtkey = self.rss_db.get_privatekey(msg.user_id)
            # TODO: signTrx with privatekey, need rumpy supported.

            if msg.user_id != MY_XIN_USER_ID:
                continue
            if msg.text.startswith(r"代发微博"):
                group_id = "3bb7a3be-d145-44af-94cf-e64b992ff8f0"
                text = msg.text[5:]
            else:
                group_id = "4e784292-6a65-471e-9f80-e91202e3358c"
                text = msg.text[3:]
            print("send_to_rum, text:", text)
            resp = self.full_rum.api.send_note(group_id=group_id, content=text)

            if "trx_id" not in resp:
                continue

            self.blaze_db.add_status(msg.message_id, "SEND_TO_RUM")

    def do_rss(self):
        for group_id in self.groups:
            self.get_group_trxs(group_id)
            self.send_group_msg_to_xin(group_id)

    def counts_trxs(self, group_id, days=-1, num=100):
        """counts trxs num of every pubkey published at that day.

        Args:
            days (int, optional): days of datetime.timedata. Defaults to -1 which means yesterday.
            num (int, optional): how many trxs to check once. Defaults to 100.

        Returns:
            {
                "data":{pubkey:num},
                "date": that_day_string
            }
        """

        thatday = datetime.datetime.now().date() + datetime.timedelta(days=days)
        counts_result = {"data": {}, "date": str(thatday)}
        while True:
            _trxs = self.full_rum.api.get_group_content(reverse=True, num=num)
            if len(_trxs) == 0:
                return counts_result
            if num >= 1000:
                return counts_result
            lastest_day = utils.timestamp_to_datetime(_trxs[-1]["TimeStamp"]).date()
            if lastest_day < thatday:
                counts = {}
                for _trx in _trxs:
                    _day = utils.timestamp_to_datetime(_trx["TimeStamp"]).date()
                    if _day == thatday:
                        _pubkey = _trx["Publisher"]
                        if _pubkey not in counts:
                            counts[_pubkey] = 1
                        else:
                            counts[_pubkey] += 1
                else:
                    counts_result["data"] = counts
                break
            else:
                logger.info(f"counts_trxs num:{num}, lastest_day:{lastest_day} thatday:{thatday}")
                num += 100

        return counts_result

    def airdrop_to_group(self, group_id, num_trxs=1, days=-1, memo=None):
        group_name = utils.group_name(self.full_rum.api.seed(group_id)["seed"])
        logger.debug(f"airdrop_to_group {group_id}, {group_name}, ...")

        counts_result = self.counts_trxs(group_id, days=days)
        date = datetime.datetime.now().date() + datetime.timedelta(days=days)
        memo = memo or f"{date} Rum 种子网络空投"
        for pubkey in counts_result["data"]:
            # trxs 条数够了
            if counts_result["data"][pubkey] < num_trxs:
                continue

            existd = (
                self.rss_db.session.query(Profile)
                .filter(
                    and_(
                        Profile.pubkey == pubkey,
                        Profile.wallet != None,
                    )
                )
                .first()
            )

            if existd:  # 有钱包
                name = existd.name
                sent = (
                    self.rss_db.session.query(AirDrop)
                    .filter(
                        and_(
                            AirDrop.mixin_id == existd.wallet,
                            AirDrop.memo == memo,
                        )
                    )
                    .first()
                )
                if sent:  # 用钱包排重，不重复空投
                    continue

                _num = str(
                    round(
                        RUM_REWARD_BASE_NUM + random.randint(1, 300) / 1000000,
                        6,
                    )
                )
                _a = {
                    "mixin_id": existd.wallet,
                    "group_id": group_id,
                    "pubkey": pubkey,
                    "num": _num,
                    "token": "RUM",
                    "memo": memo,
                    "is_sent": False,
                }
                r = self.xin.api.transfer.send_to_user(existd.wallet, RUM_ASSET_ID, _num, memo)

                if "data" in r:
                    logger.info(
                        f"""airdrop_to_group mixin_id: {existd.wallet}, num: {_num}, balance: {r.get("data").get("closing_balance") or '???'}"""
                    )
                    _a["is_sent"] = True

                self.rss_db.add(AirDrop(_a))

    def airdrop_to_node(self, num_trxs=1, days=-1, memo=None):
        for group_id in self.full_rum.api.groups_id:
            self.airdrop_to_group(group_id, num_trxs, days)

    def airdrop_to_bot(self, memo=None):
        _today = str(datetime.datetime.now().date())
        memo = memo or f"{_today} Rum 订阅器空投"
        users = self.rss_db.session.query(distinct(Rss.user_id)).all()
        for user in users:
            if len(users) < 1:
                continue
            user = user[0]
            sent = (
                self.rss_db.session.query(AirDrop).filter(and_(AirDrop.mixin_id == user, AirDrop.memo == memo)).first()
            )
            if sent:  # 用钱包排重，不重复空投
                continue

            _num = str(round(RUM_REWARD_BASE_NUM + random.randint(1, 300) / 1000000, 6))
            r = self.xin.api.transfer.send_to_user(user, RUM_ASSET_ID, _num, memo)
            _a = {
                "mixin_id": user,
                "num": _num,
                "token": "RUM",
                "memo": memo,
                "is_sent": False,
            }
            if "data" in r:
                logger.info(
                    f"""airdrop_to_bot mixin_id: {user}, num: {_num}, balance: {r.get("data").get("closing_balance") or '???'}"""
                )
                _a["is_sent"] = True

            self.rss_db.add(AirDrop(_a))

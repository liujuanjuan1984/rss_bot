import datetime
import json
import logging

from eth_account import Account
from eth_utils.hexadecimal import encode_hex
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rss.config import COMMON_ACCOUNT_PWD
from rss.modules import Base
from rss.modules.base import BaseDB
from rss.modules.keystore import KeyStore
from rss.modules.profile import Profile
from rss.modules.rss import Rss
from rss.modules.trx import Trx
from rss.modules.trx_progress import TrxProgress
from rss.modules.trx_status import TrxStatus

logger = logging.getLogger(__name__)


class RssDB(BaseDB):
    def get_rss(self, user_id, group_id):
        return self.session.query(Rss).filter(Rss.user_id == user_id).filter(Rss.group_id == group_id).first()

    def get_rss_by_user(self, user_id):
        return self.session.query(Rss.group_id).filter(Rss.user_id == user_id).all()

    def get_users_by_rss(self, group_id, is_rss):
        return self.session.query(Rss.user_id).filter(Rss.group_id == group_id).filter(Rss.is_rss == is_rss).all()

    def count_rss_by_group(self, group_id):
        return self.session.query(Rss).filter(Rss.group_id == group_id).count()

    def update_rss(self, user_id, group_id, is_rss):
        existed = self.get_rss(user_id, group_id)
        if not existed:
            _c = {
                "is_rss": is_rss,
                "user_id": user_id,
                "group_id": group_id,
            }
            self.add(Rss(_c))
        else:
            # update rss
            self.session.query(Rss).filter(Rss.user_id == user_id).filter(Rss.group_id == group_id).update(
                {"is_rss": is_rss}
            )
            self.commit()
        return True

    def get_key(self, mixin_id):
        return self.session.query(KeyStore).filter(KeyStore.user_id == mixin_id).first()

    def add_key(self, mixin_id):
        account = Account.create()
        keystore = account.encrypt(COMMON_ACCOUNT_PWD)
        _k = {
            "user_id": mixin_id,
            "keystore": json.dumps(keystore),
        }
        self.add(KeyStore(_k))
        return keystore

    def get_privatekey(self, mixin_id: str) -> str:
        key = self.get_key(mixin_id)
        if key:
            keystore = json.loads(key.keystore)
        else:
            keystore = self.add_key(mixin_id)

        pvtkey = Account.decrypt(keystore, COMMON_ACCOUNT_PWD)
        return encode_hex(pvtkey)

    def get_trx_progress(self, group_id, progress_type):
        return (
            self.session.query(TrxProgress)
            .filter(TrxProgress.group_id == group_id)
            .filter(TrxProgress.progress_type == progress_type)
            .first()
        )

    def add_trx_progress(self, group_id, trx_id, timestamp, progress_type):
        _p = {
            "progress_type": progress_type,
            "trx_id": trx_id,
            "timestamp": timestamp,
            "group_id": group_id,
        }
        self.add(TrxProgress(_p))

    def update_trx_progress(self, group_id, trx_id, timestamp, progress_type):
        if self.get_trx_progress(group_id, progress_type):
            self.session.query(TrxProgress).filter(TrxProgress.group_id == group_id).filter(
                TrxProgress.progress_type == progress_type
            ).update({"trx_id": trx_id, "timestamp": timestamp})
            self.commit()

        else:
            self.add_trx_progress(group_id, trx_id, timestamp, progress_type)

    def get_trx(self, trx_id):
        return self.session.query(Trx).filter(Trx.trx_id == trx_id).first()

    def add_trx(self, group_id, trx_id, timestamp, text):

        _p = {
            "trx_id": trx_id,
            "group_id": group_id,
            "timestamp": timestamp,
            "text": text,
        }

        self.add(Trx(_p))

    def get_trxs_later(self, group_id, timestamp):
        return self.session.query(Trx).filter(Trx.group_id == group_id).filter(Trx.timestamp > timestamp).all()

    def get_users_by_trx_sent(self, group_id, trx_id):
        return (
            self.session.query(TrxStatus.user_id)
            .filter(TrxStatus.group_id == group_id)
            .filter(TrxStatus.trx_id == trx_id)
            .all()
        )

    def add_trx_sent(self, group_id, trx_id, user_id):

        _p = {
            "trx_id": trx_id,
            "group_id": group_id,
            "user_id": user_id,
        }
        self.add(TrxStatus(_p))

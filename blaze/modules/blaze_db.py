import datetime
import logging

from blaze.modules.base import BaseDB
from blaze.modules.message import Message
from blaze.modules.status import MsgStatus

logger = logging.getLogger(__name__)


def _check_str_param(param):
    if param is None:
        return ""
    elif type(param) in [dict, list]:
        return json.dumps(param)
    elif type(param) != str:
        try:
            return str(param)
        except:
            return ""
    return param


class BlazeDB(BaseDB):
    def add_message(self, msgview, session):
        session = session or self.session

        existed = self.get_message(msgview.message_id)
        if not existed:
            _c = {
                "message_id": msgview.message_id,
                "quote_message_id": msgview.quote_message_id,
                "conversation_id": msgview.conversation_id,
                "user_id": msgview.user_id,
                "text": _check_str_param(msgview.data_decoded),
                "category": msgview.category,
                "timestamp": msgview.created_at,
            }
            self.add(Message(_c), session)
            logger.info(f"add message: {msgview.message_id}")
        else:
            logger.info(f"message already exists: {msgview.message_id}")
        return True

    def get_message(self, message_id):
        return self.session.query(Message).filter(Message.message_id == message_id).first()

    def get_messages_by_user(self, user_id):
        return self.session.query(Message).filter(Message.user_id == user_id).all()

    def get_messages_by_quote(self):
        return self.session.query(Message).filter(Message.quote_message_id != "").all()

    def get_messages_by_time(self, hours=-9):
        # 和 server 有 -8 时差。-9 也就是只处理 1 小时内的 message
        target_datetime = datetime.datetime.now() + datetime.timedelta(hours=hours)
        return self.session.query(Message).filter(Message.timestamp >= target_datetime).all()

    def get_messages_query(self, text_piece):
        if "%" not in text_piece:
            text_piece = "%{}%".format(text_piece)
        return (
            self.session.query(Message)
            .filter(Message.text.like(text_piece))
            .filter(Message.quote_message_id == "")
            .all()
        )

    def get_messages_status(self, message_id: str, status: str):
        return (
            self.session.query(MsgStatus)
            .filter(MsgStatus.message_id == message_id)
            .filter(MsgStatus.status == status)
            .first()
        )

    def add_status(self, message_id, status: str):
        existed = self.get_messages_status(message_id, status)
        if not existed:
            _c = {
                "message_id": message_id,
                "status": status,
            }
            self.add(MsgStatus(_c))
            logger.info(f"add status: {message_id},{status}")
        else:
            logger.info(f"status already exists: {message_id},{status}")
        return True

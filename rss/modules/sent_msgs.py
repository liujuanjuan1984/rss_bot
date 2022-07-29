import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from rss.modules import Base

logger = logging.getLogger(__name__)


class SentMsgs(Base):
    """the trx_id of message sent by bot."""

    __tablename__ = "sent_msgs"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    message_id = Column(String(36))  # of mixin
    trx_id = Column(String(36))  # of rum
    group_id = Column(String(36))  # of rum
    user_id = Column(String(36))  # of mixin
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

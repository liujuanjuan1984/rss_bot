import datetime
import logging

from sqlalchemy import Column, Integer, String

from blaze.modules import Base

logger = logging.getLogger(__name__)


class Message(Base):
    """mixin messages from mixin bot users"""

    __tablename__ = "messages"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    message_id = Column(String(36), unique=True)
    quote_message_id = Column(String(36), default=None)
    conversation_id = Column(String(36), default=None)
    user_id = Column(String(36), default=None)
    text = Column(String, default=None)
    category = Column(String(36), default=None)
    timestamp = Column(String, default=None)  # 消息的发送时间
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

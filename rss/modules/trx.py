import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from rss.modules import Base

logger = logging.getLogger(__name__)


class Trx(Base):
    """trxs data from rum groups which waiting to be sent."""

    __tablename__ = "trxs"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    trx_id = Column(String(36), unique=True)
    group_id = Column(String(36))
    text = Column(String)
    timestamp = Column(String)  # trx 的 timestamp
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

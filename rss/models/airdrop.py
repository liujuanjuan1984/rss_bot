import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from rss.models import Base

logger = logging.getLogger(__name__)


class AirDrop(Base):
    """the progress trx_id of rum groups"""

    logger.debug("AirDrop")

    __tablename__ = "air_drops"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    mixin_id = Column(String(36))
    group_id = Column(String(36), default=None)
    pubkey = Column(String(36), default=None)
    num = Column(String, default=None)
    token = Column(String, default=None)
    memo = Column(String)
    is_sent = Column(Boolean, default=False)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

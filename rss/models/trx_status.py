import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from rss.models import Base

logger = logging.getLogger(__name__)


class TrxStatus(Base):
    """the sent trxs data ."""

    __tablename__ = "trx_status"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    trx_id = Column(String(36))
    group_id = Column(String(36))
    user_id = Column(String(36))
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

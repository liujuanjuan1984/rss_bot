import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from rss.models import Base

logger = logging.getLogger(__name__)


class Rss(Base):
    """the rss requests from users by comments; the finally results."""

    __tablename__ = "rss"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    is_rss = Column(Boolean, default=None)
    user_id = Column(String(36), default=None)  # mixin user_id
    group_id = Column(String(36), default=None)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)

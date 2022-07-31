from sqlalchemy.orm import declarative_base

Base = declarative_base()

from blaze.models.base import BaseDB
from blaze.models.blaze_db import BlazeDB
from blaze.models.message import Message

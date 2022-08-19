from blaze.config import DB_NAME as BLAZE_DB_NAME
from blaze.models import BlazeDB
from rss.config import DB_NAME as RSS_DB_NAME
from rss.models import RssDB


blaze_db = BlazeDB(BLAZE_DB_NAME, echo=False, reset=False, init=True)
rss_db = RssDB(RSS_DB_NAME, echo=False, reset=False, init=True)

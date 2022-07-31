import datetime
import logging

from mixinsdk.clients.blaze_client import BlazeClient
from mixinsdk.clients.user_config import AppConfig
from mixinsdk.types.message import MessageView

from blaze.config import BLAZE_ZEROMESH, DB_NAME, MIXIN_KEYSTORE
from blaze.models import BlazeDB

logger = logging.getLogger(__name__)

"""
监控 mixin bot 所接收的消息，并把消息写入 db
"""


class BlazeBot:
    def __init__(self, db_name, mixin_keystore):
        self.config = AppConfig.from_payload(mixin_keystore)
        self.db = BlazeDB(db_name, echo=False, reset=False)


def message_handle_error_callback(error, details):
    logger.error("===== error_callback =====")
    logger.error(f"error: {error}")
    logger.error(f"details: {details}")


async def message_handle(message):
    global bot
    action = message["action"]

    # messages sent by bot
    if action == "ACKNOWLEDGE_MESSAGE_RECEIPT":
        # logger.info("Mixin blaze server: received the message")
        return

    if action == "LIST_PENDING_MESSAGES":
        # logger.info("Mixin blaze server: list pending message")
        return

    if action == "ERROR":
        logger.warning(message["error"])
        return

    if action != "CREATE_MESSAGE":
        return

    error = message.get("error")
    if error:
        logger.info(str(error))
        return

    msgview = MessageView.from_dict(message["data"])

    if msgview.type != "message":
        await bot.blaze.echo(msgview.message_id)
        return

    # 和 server 有 -8 时差。也就是只处理 1 小时内的 message
    if msgview.created_at <= datetime.datetime.now() + datetime.timedelta(hours=-9):
        await bot.blaze.echo(msgview.message_id)
        return
    if msgview.conversation_id in ("", None):
        await bot.blaze.echo(msgview.message_id)
        return
    if msgview.data_decoded in ("", None):
        await bot.blaze.echo(msgview.message_id)
        return
    if type(msgview.data_decoded) != str:
        await bot.blaze.echo(msgview.message_id)
        return

    print(msgview.created_at, msgview.user_id, msgview.message_id)
    if bot.db.add_message(msgview, session=bot.db.Session()):
        await bot.blaze.echo(msgview.message_id)
    return


bot = BlazeBot(DB_NAME, MIXIN_KEYSTORE)  # config.py
bot.blaze = BlazeClient(
    bot.config,
    on_message=message_handle,
    on_message_error_callback=message_handle_error_callback,
    api_base=BLAZE_ZEROMESH,
)
bot.blaze.run_forever(2)

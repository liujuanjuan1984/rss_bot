""" 

"""

from blaze.models import BlazeDB, Message
from blaze.models.status import MsgStatus

blaze = BlazeDB()

ids = blaze.session.query(MsgStatus.message_id).filter_by(status="replied").all()
for i in ids:
    print(i)
    if len(i) > 0:
        blaze.set_message_replied(i[0])

ids = blaze.session.query(MsgStatus.message_id).filter_by(status="SEND_TO_RUM").all()
for i in ids:
    print(i)
    if len(i) > 0:
        blaze.set_message_sent(i[0])

import json
import os

DB_NAME = f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/blaze_messages.db"

HTTP_DEFAULT = "https://api.mixin.one"
HTTP_ZEROMESH = "https://mixin-api.zeromesh.net"
BLAZE_DEFAULT = "wss://blaze.mixin.one"
BLAZE_ZEROMESH = "wss://mixin-blaze.zeromesh.net"

# fake data for test, please update

mixin_keystore_file = os.path.join(os.path.dirname(__file__), "mixin_keystore.json")


with open(mixin_keystore_file, "r") as f:
    MIXIN_KEYSTORE = json.loads(f.read())


print("Mixin keystore:", MIXIN_KEYSTORE)

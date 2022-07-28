import os

DB_NAME = f"sqlite:///{os.path.dirname(os.path.dirname(__file__))}/blaze_messages.db"
API_BASE_BLAZE = "wss://mixin-blaze.zeromesh.net"

# fake data for test, please update
MIXIN_KEYSTORE = {
    "pin": "123474",
    "client_id": "30789e31-ee2b-4eeb-9863-1a45e781ae2e",
    "session_id": "d92a35ea-d0e0-4670-8e10-3ccb3491e013",
    "pin_token": "q0ij-E04eCWXpq3SXzp2UXnaitt3JMwPlh1a9NsCQ3M",
    "private_key": "nxw2h201ESDA2_ReiE023M2t06qj5i2Men_SIUP2IZiwgGe0g8pAsItelRNNNgvjyIKYg0eWvtecH9essI-xqg",
}

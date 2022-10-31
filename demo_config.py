import os
from sys import exit as die

BONDY_URL = os.getenv("BONDY_URL", "ws://localhost:18080/ws")
BONDY_REALM = os.getenv("BONDY_REALM", "com.market.demo")

# RPCs
MARKET_BIDDER_ADD = "com.market.bidder.add"
MARKET_BIDDER_GONE = "com.market.bidder.gone"
MARKET_GET = "com.market.get"
MARKET_ITEM_GET = "com.market.item.get"
MARKET_ITEM_SELL = "com.market.item.sell"
MARKET_ITEM_BID = "com.market.item.bid"

# PubSubs
MARKET_ITEM_ADDED = "com.market.item.added"
MARKET_ITEM_NEW_PRICE = "com.market.item.new_price"

# Cryptosign users, their private key comes from an env var
CRYTOSIGN_PRIVATE_KEY_VARS = {
    "bot": "BOT_PRIVKEY",
    "market": "MARKET_PRIVKEY",
}


def create_transport_config(url=BONDY_URL):

    return {"type": "websocket", "url": url, "serializers": ["json"]}


def create_cryptosign_config(user_id, private_key):

    return {"cryptosign": {"authid": user_id, "privkey": private_key}}


def create_auth_config(user_id=None):

    # Cryptosign users
    private_key_var = CRYTOSIGN_PRIVATE_KEY_VARS.get(user_id)
    if private_key_var:
        private_key = os.getenv(private_key_var) or die(
            f"Missing env {private_key_var}"
        )
        return create_cryptosign_config(user_id, private_key)

    # Connect anonymously by default
    return None


def create_autobahn_component_config(url=BONDY_URL, user_id=None, realm=BONDY_REALM):

    return {
        "transports": [create_transport_config(url)],
        "authentication": create_auth_config(user_id),
        "realm": realm,
    }

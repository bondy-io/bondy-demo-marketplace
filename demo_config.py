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

# Authentication
MARKET_PRIVKEY = os.getenv("MARKET_PRIVKEY") or die("Missing env MARKET_PRIVKEY")

AUTH_MARKET = {
    "cryptosign": {
        "authid": "market",
        "privkey": MARKET_PRIVKEY,
    }
}


def create_transport_config(url=BONDY_URL):

    return {"type": "websocket", "url": url, "serializers": ["json"]}


def create_auth_config(user_id=None):

    user_configs = {
        "market": AUTH_MARKET,
    }

    # Connect anonymously by default
    return user_configs.get(user_id, None)


def create_autobahn_component_config(url=BONDY_URL, user_id=None, realm=BONDY_REALM):

    return {
        "transports": [create_transport_config(url)],
        "authentication": create_auth_config(user_id),
        "realm": realm,
    }

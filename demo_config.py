import os

BONDY_URL = os.getenv("BONDY_URL", "ws://localhost:18080/ws")
BONDY_REALM = os.getenv("BONDY_REALM", "com.market.demo")

# RPCs
MARKET_BIDDER_ADD = "com.market.bidder.added"
MARKET_BIDDER_GONE = "com.market.bidder.gone"
MARKET_GET = "com.market.get"
MARKET_ITEM_GET = "com.market.item.get"
MARKET_ITEM_SELL = "com.market.item.sell"
MARKET_ITEM_BID = "com.market.item.bid"

# PubSubs
MARKET_ITEM_ADDED = "com.market.item.added"
MARKET_ITEM_NEW_PRICE = "com.market.item.new_price"

AUTH_METHOD = os.getenv("AUTH_METHOD", "anonymous")


def create_transport_config(url=BONDY_URL):

    return {"type": "websocket", "url": url, "serializers": ["json"]}


def create_auth_config(method=AUTH_METHOD):

    AUTH_CONFIG = {"anonymous": None}

    return AUTH_CONFIG[method]


def create_autobahn_component_config(
    url=BONDY_URL, auth_method=AUTH_METHOD, realm=BONDY_REALM
):

    return {
        "transports": [create_transport_config(url)],
        "authentication": create_auth_config(auth_method),
        "realm": realm,
    }

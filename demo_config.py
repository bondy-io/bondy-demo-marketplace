import os

BONDY_URL = os.getenv("BONDY_URL", "ws://localhost:18080/ws")
BONDY_REALM = os.getenv("BONDY_REALM", "market.my")

# RPCs
MARKET_GET = "market.get"
MARKET_ITEM_SELL = "market.item.sell"
MARKET_ITEM_BID = "market.item.bid"

# PubSubs
MARKET_ITEM_ADDED = "market.item.added"
MARKET_ITEM_NEW_PRICE = "market.item.new_price"

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

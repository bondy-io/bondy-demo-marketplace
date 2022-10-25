#!/usr/bin/env python3

import signal

from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run

from demo_config import create_autobahn_component_config
from demo_config import MARKET_ITEM_ADDED
from demo_config import MARKET_GET
from demo_config import MARKET_ITEM_BID
from demo_config import MARKET_ITEM_SELL
from demo_config import MARKET_ITEM_NEW_PRICE
from item import Item


class Market:
    def __init__(self):

        ab_component_config = create_autobahn_component_config()
        self._component = Component(**ab_component_config)
        self._component.on("join", self._on_join)

        self._session = None

        self._items = {}

    def run(self):

        run([self._component])

    def _on_join(self, session, details):

        self._session = session
        self._session.register(self._get_items, MARKET_GET)
        self._session.register(self._on_new_item, MARKET_ITEM_SELL)
        self._session.register(self._on_bid, MARKET_ITEM_BID)

    def _get_items(self):

        return [item.wamp_pack() for item in self._items.values()]

    def _on_new_item(self, name, price, deadline):

        if name in self._items:
            return False

        item = Item(name, price, deadline)
        self._items[name] = item
        self._session.publish(MARKET_ITEM_ADDED, *item.wamp_pack())
        return True

    def _on_bid(self, name, bid):

        item = self._items.get(name)
        if item is None:
            return False

        if item.bid(bid):
            self._session.publish(MARKET_ITEM_NEW_PRICE, name, bid)
            return True

        else:
            return False


if __name__ == "__main__":

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    market = Market()
    market.run()

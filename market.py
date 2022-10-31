#!/usr/bin/env python3

import signal

from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run

from demo_config import create_autobahn_component_config
from demo_config import MARKET_BIDDER_ADD
from demo_config import MARKET_BIDDER_GONE
from demo_config import MARKET_ITEM_ADDED
from demo_config import MARKET_GET
from demo_config import MARKET_ITEM_GET
from demo_config import MARKET_ITEM_BID
from demo_config import MARKET_ITEM_SELL
from demo_config import MARKET_ITEM_NEW_PRICE
from demo_config import MARKET_OPENED
from item import Item


class Market:
    def __init__(self):

        ab_component_config = create_autobahn_component_config(user_id="market")
        self._component = Component(**ab_component_config)
        self._component.on("join", self._on_join)

        self._session = None

        self._items = {}
        self._bidders = set()

    def run(self):

        run([self._component])

    def _on_join(self, session, details):

        self._session = session
        self._session.register(self._get_items, MARKET_GET)
        self._session.register(self._get_item, MARKET_ITEM_GET)
        self._session.register(self._on_new_item, MARKET_ITEM_SELL)
        self._session.register(self._on_bid, MARKET_ITEM_BID)
        self._session.register(self._on_new_bidder, MARKET_BIDDER_ADD)
        self._session.register(self._on_bidder_gone, MARKET_BIDDER_GONE)

        print("Market ready to accept new items and bids")
        self._session.publish(MARKET_OPENED)

    def _on_new_bidder(self, name):
        if not name or name in self._bidders:
            return False

        else:
            print(f"New bidder: {name}")
            self._bidders.add(name)
            return True

    def _on_bidder_gone(self, name):

        if not name or name not in self._bidders:
            return

        print(f"{name} left, cancel thier bids.")
        self._bidders.remove(name)

        for item in self._items.values():
            if item.is_on_offer() and item.winner == name:
                item.winner = None

    def _get_items(self):

        return [item.wamp_pack() for item in self._items.values()]

    def _get_item(self, name):

        item = self._items.get(name)
        return item.wamp_pack() if item is not None else None

    def _on_new_item(self, name, price, deadline):

        if name in self._items:
            return False

        item = Item(name, price, deadline)
        self._items[name] = item
        print(f"New item starting at ${item.price} until {item.deadline_as_HMS()}.")
        self._session.publish(MARKET_ITEM_ADDED, **item.wamp_pack())
        return True

    def _on_bid(self, item_name, bid, bidder_name):

        if bidder_name not in self._bidders:
            return False

        item = self._items.get(item_name)
        if item is None:
            return False

        if item.bid(bid, bidder_name):
            print(f"Bid: '{item.name}' at ${item.price} from {bidder_name} ACCEPTED")
            self._session.publish(MARKET_ITEM_NEW_PRICE, **item.wamp_pack())
            return True

        else:
            print(f"Bid: '{item.name}' at ${item.price} from {bidder_name} REJECTED")
            return False


if __name__ == "__main__":

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    market = Market()
    market.run()

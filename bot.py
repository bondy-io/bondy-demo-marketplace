import signal
import time
import sys

from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run

from demo_config import create_autobahn_component_config
from demo_config import MARKET_BIDDER_ADD
from demo_config import MARKET_GET
from demo_config import MARKET_ITEM_ADDED
from demo_config import MARKET_ITEM_GET
from demo_config import MARKET_ITEM_BID
from demo_config import MARKET_ITEM_NEW_PRICE
from item import Item


class Bot:
    def __init__(self, name, incr=1.0, limit=100.0, lag=5):

        self._name = name
        self._incr = round(float(incr), 2)
        self._limit = round(float(limit) - self._incr, 2)
        self._lag = int(lag)

        ab_component_config = create_autobahn_component_config()
        self._component = Component(**ab_component_config)
        self._component.on("join", self._on_join)

        self._session = None
        self._bids = set()

    def run(self):

        run([self._component])

    async def _identify(self):

        while not self._name:
            self._name = input("Enter the name of the bot: ")
        while not await self._session.call(MARKET_BIDDER_ADD, self._name):
            self._name = input("Name already taken, enter a different name: ")

    async def _on_join(self, session, details):

        self._session = session

        await self._identify()

        print(
            f"""
{self._name} joined the '{session.realm}' marketplace.
{self._name} will try to buy any item cheaper than ${self._limit+self._incr}.
{self._name} will bid adding ${self._incr}.
To make the bot more 'human' like:
    - {self._name} will only bid one item at a time
    - It takes {self._lag}s for {self._name} to perform a bid
    - After 3 consecutive bid failutes, {self._name} gives up on the item
"""
        )

        await self._first_bids()

        self._session.subscribe(self._on_new_item, MARKET_ITEM_ADDED)
        self._session.subscribe(self._on_bid, MARKET_ITEM_NEW_PRICE)

    async def _first_bids(self):

        print(f"{self._name} queries the market...")
        market = await self._session.call(MARKET_GET)

        items = [
            item
            for item in map(Item.wamp_unpack, market)
            if item.is_on_offer() and item.price < self._limit
        ]

        n_items = len(items)
        if 0 == n_items:
            print(f"{self._name} did not find anything interesting.")
            print(f"{self._name} is waiting for new items...\n")

        else:
            print(
                f"{self._name} found {n_items} interesting item{'s' if 1 < n_items else ''}"
            )
            for item in items:
                await self._start_bidding(item.name)

    async def _start_bidding(self, item_name):

        print(f"{self._name} is looking at the item '{item_name}'")
        tries = 0
        while tries < 3:
            item_details = await self._session.call(MARKET_ITEM_GET, item_name)
            item = Item.wamp_unpack(item_details)
            if not item.is_on_offer():
                print(
                    f"'{item.name}' deadline is expired. {self._name} discard the item.\n"
                )
                return
            if self._limit < item.price:
                print(
                    f"'{item.name}' is too expensive, ${item.price}. {self._name} gives up.\n"
                )
                return
            print(f"It takes {self._lag}s for {self._name} to submit the new price...")
            time.sleep(self._lag)
            new_price = item.price + self._incr
            print(f"{self._name} bids on {item.name} at ${new_price}...")
            if await self._session.call(
                MARKET_ITEM_BID, item.name, new_price, self._name
            ):
                print(f"Bid accepted! {self._name} is happy.\n")
                return

            else:
                print(f"Bid rejected, {self._name} tries again")
                tries += 1

        print(
            f"After 3 failures, {self._name} gives up bidding on item '{item.name}'\n"
        )

    async def _on_new_item(self, name, price, deadline):

        item = Item(name, price, deadline)
        print(
            f"{self._name} is notified a new item '{name}' is on offer at ${item.price}."
        )

        if name in self._bids:
            print(f"{self._name} is already bidding on item '{name}'")
            return

        self._bids.add(name)
        await self._start_bidding(name)
        self._bids.remove(name)

    async def _on_bid(self, name, bid, deadline, winner):

        if winner == self._name:
            return

        item = Item(name, bid, deadline, winner)
        print(
            f"{self._name} is notified of a new bid at ${item.price} on time '{item.name}'"
        )
        if self._limit < item.price:
            print(f"Too expensive, {self._name} ignores the item.\n")
            return

        if name in self._bids:
            print(f"{self._name} is already bidding on item '{name}'")
            return

        self._bids.add(name)
        await self._start_bidding(name)
        self._bids.remove(name)


if __name__ == "__main__":

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    bot = Bot(*sys.argv[1:])
    bot.run()
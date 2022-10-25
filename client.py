#!/usr/bin/env python3

import signal

from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run
import txaio

from demo_config import create_autobahn_component_config
from demo_config import MARKET_GET
from demo_config import MARKET_ITEM_BID
from demo_config import MARKET_ITEM_SELL
from item import Item


class Client:
    def __init__(self):

        ab_component_config = create_autobahn_component_config()
        self._component = Component(**ab_component_config)
        self._component.on("join", self._on_join)

        self._session = None

    def run(self):

        run([self._component])

    async def _print_help(self, *args):

        print(
            """
Commands are represented by a word or its first letter.
Arguments can be provided (whitespace separated) otherwise they will be queried.

[h]help     Print this help message.

[q]uit
[e]xit      Exit the marketplace

[l]ist
[g]et       Print all the currently listed items with their details.

[s]ell [ITEM_NAME INITIAL_PRICE DEADLINE]
            Add a new item for sale at a given price. Bids are accepted within
            the given DEADLINE minutes. PRICE and DEALINE are floating numbers.

[b]id [ITEM_NAME PRICE]
            Bid on an item at a given price and tell if the offer was accepted.
            Bids are rejected if the price is an invalid number, a lower number
            than the current price or highest bid, or the bid happend after the
            deadline.
"""
        )

    async def _list_items(self, *args):

        result = await self._session.call(MARKET_GET)
        items = [Item.wamp_unpack(i) for i in result]

        names = [item.name for item in items]
        len_name = max(map(len, names), default=len("Item"))
        len_name = max(len_name, len("Item"))

        prices_str = [str(item.price) for item in items]
        len_price = max(map(len, prices_str), default=len("Price"))
        len_price = max(len_price, len("Price"))

        deadlines = map(lambda i: f"{i.deadline.astimezone():%H:%M:%S}", items)

        line = f"{{0:{len_name}}}    {{1:>{len_price}}}    {{2}}"
        print(line.format("Item", "Price", "Deadline"))
        print(line.format(len_name * "-", len_price * "-", 10 * "-"))
        for line_args in zip(names, prices_str, deadlines):
            print(line.format(*line_args))
        print()

    async def _sell(self, *args):

        if 2 < len(args):
            name = " ".join(args[:-2])
            price = args[-2]
            deadline = args[-1]

        else:
            name = " ".join(args) or input("Item name: ")
            price = float(input("Asking price: "))
            deadline = float(input("Deadline in minutes: "))

        item = Item(name, price, deadline)
        if await self._session.call(MARKET_ITEM_SELL, *item.wamp_pack()):
            print(f"Item '{item.name}' added.\n")

        else:
            print(f"Unable to add item '{item.name}'.\n")

    async def _bid(self, *args):

        if 1 < len(args):
            name = " ".join(args[:-1])
            price = args[-1]

        else:
            name = " ".join(args) or input("Item name: ")
            price = float(input("Bid: "))

        print("Bid accepted\n") if await self._session.call(
            MARKET_ITEM_BID, name, price
        ) else print("Bid rejected\n")

    async def _on_join(self, session, details):

        self._session = session

        print(f"\nWelcome to '{session.realm}' marketplace")
        await self._print_help()
        action = ""
        args = None
        while action not in ("q", "quit", "e", "exit"):

            functions = {
                "h": self._print_help,
                "help": self._print_help,
                "l": self._list_items,
                "list": self._list_items,
                "g": self._list_items,
                "get": self._list_items,
                "s": self._sell,
                "sell": self._sell,
                "b": self._bid,
                "bid": self._bid,
            }
            function = functions.get(action.lower())
            if function:
                try:
                    await function(*args)

                except BaseException as error:
                    print(f"Invalid input: {error}")

            user_input = input("> ").strip().split()
            action, *args = user_input if 0 < len(user_input) else ("",)

        print("Bye.")
        session.leave()


if __name__ == "__main__":

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Only log warnings and errors from autobahn
    txaio.use_asyncio()
    txaio.start_logging(level="warn")

    client = Client()
    client.run()

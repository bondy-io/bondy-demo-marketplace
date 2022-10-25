from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import partial


now_utc = partial(datetime.now, timezone.utc)


class Item:
    def __init__(self, name, price, deadline, winner=None):

        self.name = str(name)
        self.price = round(float(price), 2)
        try:
            # deadline from json serialization
            self.deadline = datetime.fromisoformat(deadline)

        except:
            # deadlinen from user input
            self.deadline = now_utc() + timedelta(minutes=float(deadline))

        self.winner = winner

    def bid(self, bid, bidder):

        if self.deadline < now_utc():
            return False

        new_price = round(float(bid), 2)
        if self.price < new_price:
            self.price = new_price
            self.winner = bidder
            return True

        else:
            return False

    def is_on_offer(self):

        return now_utc() < self.deadline

    ############################################################################
    # For WAMP messages

    def wamp_pack(self):

        if self.winner:
            return self.name, self.price, self.deadline.isoformat(), self.winner

        else:
            return self.name, self.price, self.deadline.isoformat()

    @classmethod
    def wamp_unpack(cls, details):

        return cls(*details)

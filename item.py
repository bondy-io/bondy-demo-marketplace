from datetime import datetime
from datetime import timedelta
from datetime import timezone
from functools import partial


now_utc = partial(datetime.now, timezone.utc)


class Item:
    def __init__(self, name, price, deadline):

        self.name = str(name)
        self.price = round(float(price), 2)
        try:
            # deadline from json serialization
            self.deadline = datetime.fromisoformat(deadline)

        except:
            # deadlinen from user input
            self.deadline = now_utc() + timedelta(minutes=float(deadline))

    def bid(self, bid):

        if self.deadline < now_utc():
            return False

        new_price = round(float(bid), 2)
        if self.price < new_price:
            self.price = new_price
            return True

        else:
            return False

    # For WAMP messages

    def wamp_pack(self):

        return [self.name, self.price, self.deadline.isoformat()]

    @classmethod
    def wamp_unpack(cls, details):

        return cls(*details)

# Bondy Demo

Simple example demonstrating the use of routed Remote Procedure Calls (RPC) and Publish/Subscribe using [Bondy](http://www.bondy.io).

## Architecture
The demo implements a simple market maker as depicted in the following diagram.

![](./assets/diagram.png)

### Actors

* User: A human using either the CLI or the Web App.
* Web App: A single page application written written in Typescript using VueJS and Autobahn JS (Browser).
* CLI: A command line interface written in Python and using Autobahn Python WAMP client.
* Bot: A microservice that allow the creation of named bots (via its CLI). Bots will automatically bid for items.
* Market: A microservice implementing a simple market maker.

See further descriptions of each actor in the sections below.


## Running the Demo

### Prerequisites

* `make` (normally present in macOS, Linux and Windows)
* Python 3.7+
* [Docker](https://www.docker.com) (Docker Desktop in case you use macOS or Windows)

### Setup

The demo environment is started by the default make target.
``` bash
% make
```

This will run Bondy and the Web App on docker (if necessary), then start the marketplace.

**Note:** Bondy takes a few seconds to start, initialize and be ready to accept connections. You should see the market script trying to reconnect until Bondy is ready. Typically, a series of logs similar to:
```
2022-10-24T12:33:12 trying transport 0 ("ws://localhost:18080/ws") using connect delay 0
2022-10-24T12:33:12 connecting once using transport type "websocket" over endpoint "tcp"
2022-10-24T12:33:12 Connection failed: TransportLost: failed to complete connection
2022-10-24T12:33:12 trying transport 0 ("ws://localhost:18080/ws") using connect delay 2.198465193966359
2022-10-24T12:33:14 connecting once using transport type "websocket" over endpoint "tcp"
```


## Interactive client

A client is available to interact with the market.
``` bash
% make client
```

It will first print the help and prompt you to enter a command.

A client can only call RPCs on the market:
* `com.market.get`: To get all the listed items.
* `com.market.item.bid`: To bid on a listed item.
* `com.market.item.sell` To put a new item on the market place.

Under the hood it will call `com.market.bidder.add` to identify itself as a bidder.
On exit it calls `com.market.bidder.gone` to dereference itself as a bidder.

Once you are familiar with the marketplace, listing, selling and bidding on items, you can try and compete against a bot.

## Bot

A bot has a name (`BOT_NAME` variable, default: _Bob_) and is configured to:
* buy any item cheaper than a given price (`BOT_LIMIT` variable, default: $10).
* bid adding a given amount to the highest bid (`BOT_INCR` variable, default $1).
* take some time (`BOT_LAG` variable, default: 5s) to perform the bid, i.e. a lag between computing the bid price and actually bidding.
``` bash
% make bot

% make bot BOT_NAME=Alice BOT_LIMIT=12 BOT_INCR=2
```

**Note:** A bot gives up on an item after 3 consecutive bidding failures.

A bot subscribes to 2 topics:
* `com.market.item.added`: To know when a new item is on offer.
* `com.market.item.new_price`: To know when there is a new accepted bid.
* `com.market.opened`: To know when the market is connected and ready to accept bids.

Similarly to the client, it calls some RPCs to try and win some items:
* `com.market.bidder.add` to identify itself as a bidder.
* `com.market.get`: To get all the listed items when it joins the marketplace.
* `com.market.item.bid`: To bid on a listed item.
* `com.market.item.get`: To get the details of a specific item for optimum bid.

Once you are familiar with the log printed by the bot, you can try and have several of them competing against each other.

### Launching many bots

You can simulate a busy market by launching many bots:
``` bash
% make many_bots
```

The `many_bots` target launches 4 bots that bid with different increments and lags.
They all have a limit at $10,000.
* Alice takes 0.3s to bid and increments by $3.
* Tom takes 0.5s to bid and increments by $5.
* Mary takes 0.7s to bid and increments by $7.
* Victor takes 1.1s to bid and increments by $11.

#### Hitting the deadline

If you sale an item at $1, the bots will compete for quite a while.
You can hit the deadline by selling an item for 1 minute.

Here from the interactive client, a bike is sold at $1 for a minute:
```
% make client
...
> sell bike 1 1
```

From the market logs you can see the bots competing, some bids are rejected and in the end Mary wins:
```
New item starting at $1.0 until 10:08:23.
Bid: 'bike' at $4.0 from Alice ACCEPTED
Bid: 'bike' at $6.0 from Tom ACCEPTED
Bid: 'bike' at $8.0 from Mary ACCEPTED
...
Bid: 'bike' at $37.0 from Alice ACCEPTED
Bid: 'bike' at $37.0 from Victor REJECTED   <--- Nope
Bid: 'bike' at $42.0 from Tom ACCEPTED
...

Bid: 'bike' at $587.0 from Alice ACCEPTED
Bid: 'bike' at $588.0 from Mary ACCEPTED    <--- Winner!
Bid: 'bike' at $588.0 from Victor REJECTED  <--- Too late
Bid: 'bike' at $588.0 from Alice REJECTED   <--- Too late
Bid: 'bike' at $588.0 from Tom REJECTED     <--- Too late
```

This is confirmed when listing the items:
```
> list
Item    Price    Deadline    Winner
----    -----    --------    ------
bike    588.0    10:08:23    Mary
```

#### Hitting the limit

Similarly by selling an item close to the limit, one of the bot will win before the deadline and the others will give up.

Here from the interactive client, a car is sold at $9950 for 10 minutes:
```
% make client
...
> sell car 9950 10
```

Very quicky the bids stop:
```
...
Bid: 'car' at $9993.0 from Tom ACCEPTED
Bid: 'car' at $9993.0 from Mary REJECTED
Bid: 'car' at $9996.0 from Victor ACCEPTED
Bid: 'car' at $9996.0 from Alice REJECTED
Bid: 'car' at $9999.0 from Alice ACCEPTED
Bid: 'car' at $10000.0 from Mary ACCEPTED   <--- winner!
```

And Mary won again!
```
> list
Item      Price    Deadline    Winner
----    -------    --------    ------
bike      588.0    10:08:23    Mary
car     10000.0    10:29:55    Mary
```

## Bondy

You run the Bondy router from the `make` target: `bondy_docker`.
``` bash
% make bondy_docker
```

## Market

Run the marketplace from the `make` target: `market`
``` bash
% make market
```

This will create the python virtual environment with all the dependencies required to run the script.
The script then connects to Bondy and registers the following URIs:
* `com.market.bidder.add`: When a new bigger joins, it has to give a name to be able to bid.
* `com.market.bidder.gone`: When a client gently leave the market, i.e. no errors or interuptions.
* `com.market.get`: To get all the listed items.
* `com.market.item.bid`: To bid on a listed item.
* `com.market.item.get`: To get the details of a specific item.
* `com.market.item.sell` To put a new item on the market place.

The market publishes the following topics:
* `com.market.item.added`: When a new item is on offer.
* `com.market.item.new_price`: When a bid was accepted.
* `com.market.opened`: When `market` is connected and has registered the RPC URIs, it publishes this topic to let the listeners it is ready to accept calls.

## Troubleshooting

### docker: Error response from daemon: Conflict.
There is already a container with `bondy-demo` name running in Docker.
As the message says, remove the duplicate and start over.

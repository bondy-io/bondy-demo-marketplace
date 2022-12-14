import autobahn from "autobahn";
import nacl from "tweetnacl";

export default {

    getAnonymousConnection(url, realm) {
        console.log(`Running AutobahnJS ${autobahn.version}`);
        console.log(`Wamp Router Url='${url}'`);
        console.log(`Wamp Realm='${realm}'`);
        console.log("Trying to connect ...");
        return new autobahn.Connection({
            url: url,
            realm: realm,
            authmethods: ["anonymous"]
        });
    },

    getCryptosignConnection(url, realm, username, pkey) {
        console.log(`Running AutobahnJS ${autobahn.version}`);
        console.log(`Wamp Router Url='${url}'`);
        console.log(`Wamp Realm='${realm}'`);
        console.log(`username='${username}'`);
        console.log(`pkey='${pkey}'`);
        console.log("Trying to connect ...");
        return new autobahn.Connection({
            url: url,
            realm: realm,
            authextra: {
                pubkey: pkey,
                trustroot: null,
                challenge: null,
                channel_binding: null
            },
            authmethods: ["cryptosign"],
            authid: username,
            onchallenge: function (session, method, extra) {
                console.log(`Authenticating using '${method}'`);
                console.log(`On Challenge Called with extra ${JSON.stringify(extra)}`);
                let appPrivkey = autobahn.util.htob(
                    "4ffddd896a530ce5ee8c86b83b0d31835490a97a9cd718cb2f09c9fd31c4a7d71766c9e6ec7d7b354fd7a2e4542753a23cae0b901228305621e5b8713299ccdd"
                );
                let challenge = autobahn.util.htob(extra.challenge);
                let signature = nacl.sign.detached(challenge, appPrivkey);
                return autobahn.util.btoh(signature);
            }
        });
    },

    // List of items; an items has a name, a deadline, an asking price and the current highest bid (0: no bids)
    async getMarket(session, setItemsFun, setErrorFun) {
        // only to emulate timing retrieving maketplate items and see the "loading" banner in the table
        await new Promise((r) => setTimeout(r, 2000));

        session
            .call("com.market.get", [], {}, { timeout: 5000 })
            .then(
                function (res) {
                    setItemsFun(res);
                },
                function (err) {
                    setErrorFun(err);
                }
            );
    },

    // It allows to do a subscription to the intereted topics
    async subscribe(session, subsConfig) {
        subsConfig.forEach(element => {
            let topic = element[0];
            let onFun = element[1];
            session
                .subscribe(topic, onFun, { match: "exact" })
                .then(
                    () => {
                        console.log(`Subscribed to topic '${topic}' successfully`);
                    },
                    (err) => {
                        console.log(
                            `Subscription to topic '${topic}' failed with error: ${err}`
                        );
                    }
                );
        });
    },

    // - true: the item is registered and bids are possible.
    // - false: Something went wrong (duplicate name, invalid price or deadline???)
    // item:
    //  - name (string) Name of the item
    //  - price (float) Asking price
    //  - deadline (integer) Deadline in minutes
    sellItem(session, item, setSuccessFun, setErrorFun) {
        session
            .call("com.market.item.sell", [item.name, item.price, item.deadline], {}, { timeout: 5000 })
            .then(
                function (res) {
                    setSuccessFun(res);
                },
                function (err) {
                    setErrorFun(err);
                }
            );
    },

    addBidder(session, bidderName, setSuccessFun, setErrorFun) {
        session
            .call("com.market.bidder.add", [bidderName], {}, { timeout: 5000 })
            .then(
                function (res) {
                    setSuccessFun(res);
                },
                function (err) {
                    setErrorFun(err);
                }
            );
    },

    removeBidder(session, bidderName, setSuccessFun, setErrorFun) {
        session
            .call("com.market.bidder.gone", [bidderName], {}, { timeout: 5000 })
            .then(
                function (res) {
                    setSuccessFun(res);
                },
                function (err) {
                    setErrorFun(err);
                }
            );
    },

    // - true: Bid accepted, i.e. highest price
    // - false: Bid rejected (not highest, item not on sell anymore???)
    // item:
    //  - name (string) Name of the item
    //  - price (float) Bid
    //  - bidder (String) Name of the bidder
    bidItem(session, item, setSuccessFun, setErrorFun) {
        session
            .call("com.market.item.bid", [item.name, item.new_price, item.bidder], {}, { timeout: 5000 })
            .then(
                function (res) {
                    setSuccessFun(res);
                },
                function (err) {
                    setErrorFun(err);
                }
            );
    }

}
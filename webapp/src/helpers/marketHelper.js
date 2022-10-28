import autobahn from "autobahn";
import nacl from "tweetnacl";

export default {

    getAnonymousConnection(url, realm) {
        console.log("-----------------------");
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
        console.log("-----------------------");
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
        // only to emulate timing retrieving maketplate items
        await new Promise((r) => setTimeout(r, 2000));

        let options = {
            timeout: 5000,
            //retry,disclose_me
        };

        session
            .call("com.market.get", [], {}, options)
            .then(
                function (res) {
                    // console.log("-----------------------");
                    // console.log(`Response OK. Items length: ${res.length}`);
                    // console.log(JSON.stringify(res, undefined, 2))
                    setItemsFun(res);
                },
                function (err) {
                    // console.log("-----------------------");
                    // console.log(`Call has failed with error: ${JSON.stringify(err, undefined, 2)}`);
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
                        console.log("-----------------------");
                        console.log(`Subscribed to topic '${topic}' successfully`);
                    },
                    (err) => {
                        console.log("-----------------------");
                        console.log(
                            `Subscription to topic '${topic}' failed with error: ${err}`
                        );
                    }
                );
        });
    },

    // - true: the item is registered and bids are possible.
    // - false: Something went wrong (duplicate name, invalid price or deadline…)
    // item:
    //  - name (string) Name of the item
    //  - price (float) Asking price
    //  - deadline (integer) Deadline in minutes
    sellItem(session, item, setSuccessFun, setErrorFun) {
        let options = {
            timeout: 5000,
        };
        // console.log(`Item to sell: ${JSON.stringify(item, undefined, 2)}`);

        session
            .call("com.market.item.sell", [item.name, item.price, item.deadline], {}, options)
            .then(
                function (res) {
                    // console.log("-----------------------");
                    // console.log(`Response OK: ${res}`);
                    setSuccessFun(res);
                },
                function (err) {
                    // console.log("-----------------------");
                    // console.log(`Call has failed with error: ${JSON.stringify(err, undefined, 2)}`);
                    setErrorFun(err);
                }
            );
    },

    // - true: Bid accepted, i.e. highest price
    // - false: Bid rejected (not highest, item not on sell anymore…)
    // item:
    //  - name (string) Name of the item
    //  - price (float) Bid
    //  - bidderName (String) Name of the bidder
    bidItem(session, item, bidderName, setSuccessFun, setErrorFun) {
        let options = {
            timeout: 5000,
        };
        // console.log(`Item to bid: ${JSON.stringify(item, undefined, 2)}`);

        session
            .call("com.market.item.bid", [item.name, item.price, bidderName], {}, options)
            .then(
                function (res) {
                    // console.log("-----------------------");
                    // console.log(`Response OK: ${res}`);
                    setSuccessFun(res);
                },
                function (err) {
                    // console.log("-----------------------");
                    // console.log(`Call has failed with error: ${JSON.stringify(err, undefined, 2)}`);
                    setErrorFun(err);
                }
            );
    }

}
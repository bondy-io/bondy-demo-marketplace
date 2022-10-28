<template>
  <v-card>
    <div align="right">
      <v-chip class="ma-2" color="blue" label outlined pilled>
        <v-icon dark @click="signup()"> mdi-account-circle-outline </v-icon>
        &nbsp;{{ bidderName }}
      </v-chip>
    </div>
    <v-data-table
      :headers="headers"
      :items="items"
      sort-by="name"
      class="elevation-1"
      :loading="loading"
      loading-text="Loading... Please wait"
      :search="search"
    >
      <template v-slot:[`item.winner`]="{ item }">
        <v-chip :color="getColorWinner(item.winner)">
          <v-icon left> mdi-account-circle-outline </v-icon>
          {{ item.winner }}
        </v-chip>
      </template>
      <template v-slot:top>
        <v-toolbar flat>
          <v-toolbar-title>Bondy Marketplace</v-toolbar-title>
          <v-divider class="mx-4" inset vertical></v-divider>
          <v-spacer></v-spacer>
          <v-card-title>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Search"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-dialog v-model="dialog" max-width="500px">
            <template v-slot:activator="{ on, attrs }">
              <v-btn color="primary" dark class="mb-2" v-bind="attrs" v-on="on">
                Sell Item
              </v-btn>
            </template>
            <v-card>
              <v-card-title>
                <span class="text-h5"
                  >Please, fill the data for the item to sell</span
                >
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="8">
                      <v-text-field
                        v-model="editedItem.name"
                        label="Name"
                        counter="25"
                        maxlength="25"
                        :rules="[
                          () =>
                            !!editedItem.name || 'The item name is required',
                        ]"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.price"
                        label="Price"
                        prefix="$"
                        type="number"
                        :rules="[
                          () =>
                            !!editedItem.price || 'The item price is required',
                        ]"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="16" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.deadline"
                        label="Deadline"
                        suffix="minutes"
                        type="number"
                        :rules="[
                          () =>
                            !!editedItem.deadline ||
                            'The item deadline is required',
                        ]"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>

              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="close">
                  Cancel
                </v-btn>
                <v-btn color="blue darken-1" text @click="save"> Save </v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dialogBid" max-width="500px">
            <v-card>
              <v-card-title class="text-h5"
                >Please, enter the new price for&nbsp;
                <span class="text-h5" style="color: orange">{{
                  editedItem.name
                }}</span></v-card-title
              >
              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="7">
                      <v-text-field
                        v-model="editedItem.price"
                        label="Highest Price"
                        readonly
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.new_price"
                        label="Price"
                        prefix="$"
                        type="number"
                        :rules="[
                          () => !!editedItem.price || 'The price is required',
                        ]"
                      ></v-text-field>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" text @click="closeBid"
                  >Cancel</v-btn
                >
                <v-btn color="blue darken-1" text @click="bidItemConfirm"
                  >Bid</v-btn
                >
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
          <v-dialog v-model="dialogSignUp" max-width="210px">
            <v-card>
              <v-card-text>
                <v-text-field
                  v-model="bidderName"
                  label="Your bidder name"
                  counter="20"
                  maxlength="20"
                  :rules="[
                    () => !!bidderName || 'The bidder name is required',
                  ]"
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-btn color="blue darken-1" text @click="closeSignUp"
                  >Cancel</v-btn
                >
                <v-btn color="blue darken-1" text @click="signUpConfirm"
                  >Sign Up</v-btn
                >
                <v-spacer></v-spacer>
              </v-card-actions>
            </v-card>
          </v-dialog>
        </v-toolbar>
      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <v-icon small class="mr-2" @click="bidItem(item)">
          mdi-shopping
        </v-icon>
      </template>
      <template v-slot:no-data> No items to show </template>
    </v-data-table>
    <v-alert type="error" v-model="alertError" dismissible elevation="2">
      {{ showErrorMsg }}
    </v-alert>
    <v-alert type="info" v-model="alertInfo" dismissible elevation="2">
      {{ showInfoMsg }}
    </v-alert>
    <v-alert type="success" v-model="alertSuccess" dismissible elevation="2">
      {{ showSuccessMsg }}
    </v-alert>
  </v-card>
</template>
<script>
import { MarketHelper } from "@/helpers/mainExports.js";

export default {
  data: () => ({
    dialog: false,
    dialogBid: false,
    dialogSignUp: false,
    alertError: false,
    errorMsg: "",
    alertInfo: false,
    infoMsg: "",
    alertSuccess: false,
    successMsg: "",
    search: "",
    headers: [
      { text: "Item", align: "start", value: "name" },
      { text: "Highest Price", value: "price" },
      { text: "Deadline", value: "deadline" },
      { text: "Bidder", value: "winner" },
      { text: "Winner", value: "winner" },
      { text: "Bid", value: "actions", sortable: false },
    ],
    items: [],
    editedIndex: -1,
    bidderName: null,
    editedItem: {
      name: "",
      price: null,
      deadline: null,
      winner: "",
      new_price: null,
    },
    defaultItem: {
      name: "",
      price: null,
      deadline: null,
      winner: "",
      new_price: null,
    },
    loading: false,
    // autobahn
    url: "ws://localhost:18081/ws",
    realm: "com.market.demo",
    username: "webapp",
    publicKey:
      "1766c9e6ec7d7b354fd7a2e4542753a23cae0b901228305621e5b8713299ccdd",
    // autobahn connection
    connection: null,
    // established session
    session: null,
    // List with the item name, a deadline, the asking price
    // Published every time a new item is posted.
    itemAddedTopic: "com.market.item.added",
    // List with the item name and the new price
    // Published at every new successful bid.
    itemPriceChangedTopic: "com.market.item.new_price",
    itemSoldTopic: "com.market.item.sold",
  }),

  computed: {
    showErrorMsg() {
      return this.errorMsg;
    },
    showInfoMsg() {
      return this.infoMsg;
    },
    showSuccessMsg() {
      return this.successMsg;
    },
  },

  watch: {
    dialog(val) {
      val || this.close();
    },
    dialogBid(val) {
      val || this.closeBid();
    },
    dialogSignUp(val) {
      val || this.closeSignUp();
    },
    alertInfo(new_val) {
      if (new_val) {
        setTimeout(() => {
          this.alertInfo = false;
        }, 5000);
      }
    },
    alertSuccess(new_val) {
      if (new_val) {
        setTimeout(() => {
          this.alertSuccess = false;
        }, 6000);
      }
    },
    alertError(new_val) {
      if (new_val) {
        setTimeout(() => {
          this.alertError = false;
        }, 8000);
      }
    },
  },

  created() {
    console.log("Component created");
    this.loading = true;
    // initialize with the retrieved items
    this.connection = this.inititialize(
      this.url,
      this.realm,
      this.itemAddedTopic,
      this.itemPriceChangedTopic,
      this.itemSoldTopic
    );
  },

  beforeDestroy() {
    console.log("Component Destroyed");
    this.connection.close("wamp.goodbye.normal", "Bondy Maketplace good bye");
    this.session = null;
    this.connection = null;
  },

  methods: {
    inititialize(url, realm, itemAddedTopic, itemPriceChangedTopic, itemSoldTopic) {
      // const connection = MarketHelper.getAnonymousConnection(url, realm);
      const connection = MarketHelper.getCryptosignConnection(
        url,
        realm,
        this.username,
        this.publicKey
      );

      // component reference to be able to access data and methods
      const self = this;

      connection.onopen = function (session, details) {
        console.log(`Connected : ${JSON.stringify(details, undefined, 2)}`);
        console.log("-----------------------");

        self.session = session;

        // retrieve and load the market items
        MarketHelper.getMarket(
          session,
          function (items) {
            self.items = items;
            self.loading = false;
          },
          function (error) {
            self.setError(error);
            self.loading = false;
          }
        );

        // subscriptions
        MarketHelper.subscribe(session, [
          [itemAddedTopic, self.onItemAdded],
          [itemPriceChangedTopic, self.onItemChanged],
          [itemSoldTopic, self.onItemChanged],
        ]);
      };

      connection.onclose = function (reason, details) {
        console.log(
          `Connection lost: ${reason}  details: ${JSON.stringify(
            details,
            undefined,
            2
          )}`
        );
        console.log("-----------------------");
      };

      // open the connection
      connection.open();
      return connection;
    },

    signup() {
      if (this.bidderName == null) {
        this.dialogSignUp = true;
      }
    },

    getColorWinner(winner) {
      if (!winner) return "black";
      if (winner == "Bob") return "green";
      else return "blue";
    },

    onItemAdded(args, argsKW, details) {
      // item data is received in the argsKW!
      console.log("-----------------------");
      console.log(`Item has been added. args ${JSON.stringify(
        args,
        undefined,
        2
      )}
                argsKW ${JSON.stringify(argsKW, undefined, 2)}
                details: ${JSON.stringify(details, undefined, 2)}`);
      let item = Object.assign(
        {},
        {
          name: argsKW.name,
          price: argsKW.price,
          deadline: argsKW.deadline,
        }
      );
      this.items.push(item);
      this.infoMsg = `The item ${item.name} has been added`;
      this.alertInfo = true;
    },

    onItemChanged(args, argsKW, details) {
      // item data is received in the argsKW!
      console.log("-----------------------");
      console.log(`Item has been changed. args ${JSON.stringify(
        args,
        undefined,
        2
      )}
                argsKW ${JSON.stringify(argsKW, undefined, 2)}
                details: ${JSON.stringify(details, undefined, 2)}`);
      let item = Object.assign(
        {},
        {
          name: argsKW.name,
          price: argsKW.price,
          deadline: argsKW.deadline,
          winner: argsKW.winner,
        }
      );
      let index = this.items.findIndex((item) => item.name == argsKW.name);
      Object.assign(this.items[index], item);
      this.infoMsg = `The item ${item.name} has been changed`;
      this.alertInfo = true;
    },

    bidItem(item) {
      if (this.bidderName != null) {
        this.editedIndex = this.items.indexOf(item);
        this.editedItem = Object.assign({}, item);
        this.dialogBid = true;
      } else {
        this.setError("You must be registered to bid an item!");
      }
    },

    bidItemConfirm() {
      MarketHelper.bidItem(
        this.session,
        this.editedItem,
        this.bidderName,
        this.setBidItemResult,
        this.setError
      );
      this.closeBid();
    },

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    closeBid() {
      this.dialogBid = false;
      this.$nextTick(() => {
        this.editedItem = Object.assign({}, this.defaultItem);
        this.editedIndex = -1;
      });
    },

    signUpConfirm() {
      // register a bidder
      MarketHelper.addBidder(
        this.session,
        this.bidderName,
        this.setSignUpResult,
        this.setError
      );
      this.closeSignUp();
    },

    setSignUpResult(res) {
      this.closeSignUp;
      if (!res) {
        this.errorMsg = `Unable to register ${this.bidderName}`;
        this.alertError = true;
        this.bidderName = null;
      }
    },

    closeSignUp() {
      this.dialogSignUp = false;
    },

    setError(error) {
      this.errorMsg = JSON.stringify(error, undefined, 2);
      this.alertError = true;
    },

    setBidItemResult(result) {
      if (result) {
        this.successMsg = "Bid accepted, i.e. highest price";
        this.alertSuccess = true;
      } else {
        this.infoMsg =
          "Bid rejected (not highest, item not on sell anymore ...)";
        this.alertInfo = true;
      }
    },

    setSellItemResult(result) {
      if (result) {
        this.successMsg = "The item was registered and bids are possible";
        this.alertSuccess = true;
      } else {
        this.infoMsg =
          "Something went wrong (duplicate name, invalid price or deadline…)";
        this.alertInfo = true;
      }
    },

    save() {
      if (this.editedIndex == -1) {
        MarketHelper.sellItem(
          this.session,
          this.editedItem,
          this.setSellItemResult,
          this.setError
        );
      }
      this.close();
    },
  },
};
</script>
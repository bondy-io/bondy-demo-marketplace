<template>
  <v-card>
    <v-alert type="error" v-model="alertError" dismissible elevation="2">
      {{ showErrorMsg }}
    </v-alert>
    <v-alert type="info" v-model="alertInfo" dismissible elevation="2">
      {{ showInfoMsg }}
    </v-alert>
    <v-alert type="success" v-model="alertSuccess" dismissible elevation="2">
      {{ showSuccessMsg }}
    </v-alert>
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
        <v-chip :color="getColor(item.winner)">
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
                <span class="text-h5">Item to Sell</span>
              </v-card-title>

              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.name"
                        label="Name"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.price"
                        label="Price"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="16" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.deadline"
                        label="Deadline"
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
                >Please, enter your name and the price</v-card-title
              >
              <v-card-text>
                <v-container>
                  <v-row>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.name"
                        label="Name"
                        readonly
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="bidderName"
                        label="Bidder"
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" sm="6" md="4">
                      <v-text-field
                        v-model="editedItem.price"
                        label="Price"
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
        </v-toolbar>
      </template>
      <template v-slot:[`item.actions`]="{ item }">
        <v-icon small class="mr-2" @click="bidItem(item)">
          mdi-shopping
        </v-icon>
      </template>
      <template v-slot:no-data> No items to show </template>
    </v-data-table>
  </v-card>
</template>
<script>
import { MarketHelper } from '@/helpers/mainExports.js'

export default {
  data: () => ({
    dialog: false,
    dialogBid: false,
    alertError: false,
    errorMsg: "",
    alertInfo: false,
    infoMsg: "",
    alertSuccess: false,
    successMsg: "",
    search: "",
    headers: [
      { text: "Item", align: "start", value: "name" },
      { text: "Price", value: "price" },
      { text: "Deadline", value: "deadline" },
      { text: "Winner", value: "winner" },
      { text: "Bid", value: "actions", sortable: false },
    ],
    items: [],
    editedIndex: -1,
    bidderName: "your name",
    editedItem: {
      name: "",
      price: null,
      deadline: null,
      winner: "",
    },
    defaultItem: {
      name: "",
      price: null,
      deadline: null,
      winner: "",
    },
    loading: false,
    // autobahn
    url: "ws://localhost:18081/ws",
    realm: "com.market.demo",
    username: "webapp",
    publicKey: "1766c9e6ec7d7b354fd7a2e4542753a23cae0b901228305621e5b8713299ccdd",
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
      this.itemPriceChangedTopic
    );
  },

  beforeDestroy() {
    console.log("Component Destroyed");
    this.connection.close("wamp.goodbye.normal", "Bondy Maketplace good bye");
    this.session = null;
    this.connection = null;
  },

  methods: {
    inititialize(url, realm, itemAddedTopic, itemPriceChangedTopic) {
      
      // const connection = MarketHelper.getAnonymousConnection(url, realm);
      const connection = MarketHelper.getCryptosignConnection(url, realm, this.username, this.publicKey);

      // component reference to be able to access data and methods
      const self = this;

      connection.onopen = function (session, details) {
        console.log(`Connected: ${JSON.stringify(details, undefined, 2)}`);
        console.log("-----------------------");

        self.session = session;

        // retrieve and load the market items
        self.getItems(session, self);

        // subscriptions
        MarketHelper.subscribe(session, [
          [itemAddedTopic, self.onItemAdded],
          [itemPriceChangedTopic, self.onItemChanged],
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

    getItems(session, self) {
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
    },

    getColor(winner) {
      if (!winner) return "dark";
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
      this.editedIndex = this.items.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialogBid = true;
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
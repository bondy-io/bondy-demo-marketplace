<template>
  <v-app>
    <v-app-bar
      app
      color="dark"
    >
      <div class="d-flex align-center">

        <v-img
          alt="Bondy Marketplace"
          class="shrink mt-1 hidden-sm-and-down"
          contain
          min-width="100"
          src="./assets/bondy_bg.png"
          width="100"
        />
      </div>

      <v-spacer></v-spacer>

      <v-btn
        href="https://github.com/Leapsight/bondy"
        target="_blank"
        text
      >
        <span class="mr-2">GitHub</span>
        <v-icon>mdi-open-in-new</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main>
      <Market/>
    </v-main>
  </v-app>
</template>

<script>
import Market from './components/marketPlace';

export default {
  name: 'App',

  components: {
    Market,
  },

  data: () => ({
    //
  }),
};
</script>

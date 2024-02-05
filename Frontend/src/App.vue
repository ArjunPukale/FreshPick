<template>
  <!-- Navigation bar -->
  <Nav v-if="this.$store.state.userType == 'N'" />
  <AdminNav v-else />
  <!-- Navigation bar ends -->

  <!-- Home Content -->
  <div style="margin-top: 70px">
    <router-view />
  </div>
  <!-- Home cotent ends -->
</template>

<script>
import Nav from "./components/Nav-bar.vue";
import AdminNav from "./components/Admin-Nav-bar.vue";

export default {
  name: "App",
  components: {
    Nav,
    AdminNav,
  },
};
</script>

<style>
nav {
  background-color: #cbfaa2;
}
body {
  background-color: beige;
}
nav.admin {
  background-color: darkkhaki; /* Background color */
}
</style>

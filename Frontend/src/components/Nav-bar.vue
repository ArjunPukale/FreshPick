<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light fixed-top">
      <div class="container-fluid">
        <!-- Brand Name (Freshpick) on the left -->

        <router-link to="/" class="navbar-brand">Freshpick</router-link>
        <!-- Add a button for small screens -->
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Navigation Links on the left (hidden on small screens) -->
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li v-if="isUserLoggedIn" class="nav-item">
              <!-- <a class="nav-link" href="#">Basket</a> -->
              <router-link to="/basket" class="nav-link">Basket</router-link>
            </li>
            <li v-if="isUserLoggedIn" class="nav-item">
              <router-link to="/orders" class="nav-link">Orders</router-link>
            </li>
          </ul>
        </div>

        <!-- Logout link on the right -->
        <ul class="navbar-nav ml-auto">
          <li v-if="isUserLoggedIn" class="nav-item">
            <a @click="logout" class="nav-link">Logout</a>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>
<style scoped>
.nav-link {
  cursor: pointer;
}
</style>
<script>
export default {
  name: "Nav-bar",
  computed: {
    isUserLoggedIn() {
      return this.$store.state.user != null;
    },
  },
  methods: {
    logout() {
      this.$store.commit("user", null);
    },
  },
};
</script>

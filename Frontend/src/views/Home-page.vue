<template>
  <div v-if="this.$store.state.user">
    <div class="header">
      <h3>Welcome {{ this.$store.state.user.firstName }}</h3>
    </div>
    <!-- <h1>Welcome {{ this.$store.state.user.firstName }}</h1> -->
    <!--Search Box-->
    <searchBarBasic />
    <!--Search Box ends-->
    <productDisplayHome
      v-if="this.specificCatDisplay == false"
      :categoryDisplay="categoryDisplay"
    />
    <productDisplayCategory
      v-else
      :specifiedCatId="specificCat"
      :allCategoryDisplay="allCategoryDisplay"
    />
  </div>
  <div v-else class="col-md-6 offset-md-3 text-center" style="margin-top: 70px">
    <h1>Welcome to Freshpick</h1>
    <p>Your go-to online grocery shopping platform.</p>
    <p>Please log in or register to get started.</p>

    <!-- Login Button -->

    <router-link to="/login" class="btn btn-primary btn-lg">Login</router-link>

    <!-- Register Option -->
    <p class="mt-3">
      Don't have an account? <router-link to="/register">Register</router-link>
    </p>
  </div>
</template>
<script>
import searchBarBasic from "@/components/search-bar-basic.vue";
import productDisplayHome from "@/components/product-display-home.vue";
import productDisplayCategory from "@/components/product-display-category.vue";
export default {
  name: "Home-page",
  data() {
    return {
      specificCatDisplay: false,
      specificCat: null,
    };
  },
  methods: {
    categoryDisplay(catId) {
      this.specificCatDisplay = true;
      this.specificCat = catId;
    },
    allCategoryDisplay() {
      this.specificCatDisplay = false;
      this.specificCat = null;
    },
  },
  components: {
    searchBarBasic,
    productDisplayHome,
    productDisplayCategory,
  },
};
</script>
<style>
.header {
  margin-top: 70px;
  margin-left: 15px;
}
</style>

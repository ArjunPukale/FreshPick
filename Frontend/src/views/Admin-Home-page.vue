<template>
  <div v-if="this.$store.state.user">
    <div class="header">
      <h3>Welcome Admin {{ this.$store.state.user.firstName }}</h3>
      <adminDashboard />
      <adminReports />
    </div>
  </div>
  <div v-else class="col-md-6 offset-md-3 text-center" style="margin-top: 70px">
    <h1>Welcome to Freshpick Admin</h1>
    <p>Please log in to get started.</p>

    <!-- Login Button -->

    <router-link to="/admin/login" class="btn btn-primary btn-lg"
      >Admin Login</router-link
    >
  </div>
</template>
<script>
import apiRequest from "@/api";
import adminDashboard from "@/components/Admin-Dashboard.vue";
import adminReports from "@/components/Admin-Reports.vue";
export default {
  name: "Admin-Home-page",
  data() {
    return {
      categories: null,
      products: null,
    };
  },
  async created() {
    // fetch inventory data from api
    const userData = { username: this.$store.state.user.username };
    try {
      const responseData = await apiRequest(
        "api/inventory?username=" +
          encodeURIComponent(this.$store.state.user.username),
        "GET",
        userData,
        true
      );
      if (responseData.categories) {
        this.$store.commit("setCategoryMaster", responseData.categories);
        this.categories = this.$store.state.categoryMaster;
      }
      if (responseData.products) {
        this.$store.commit("setProductMaster", responseData.products);
        this.products = this.$store.state.productMaster;
      }
    } catch (error) {
      console.log(error);
    }
  },
  methods: {},
  components: {
    adminDashboard,
    adminReports,
  },
};
</script>
<style>
.header {
  margin-top: 70px;
  margin-left: 15px;
}
</style>

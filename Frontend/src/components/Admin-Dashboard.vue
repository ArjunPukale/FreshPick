<template>
    <div class="container-fluid" style="margin-top:55px;">
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="text-left">Summaries</h2>
            </div>
        </div>
        <div class="row" style="display:inline-flex;">
            <div class="col-sm-4">
                <div class="card h-100">
                    <div class="card-body d-flex flex-column justify-content-between">
                        <h5 class="card-title">Total Products</h5>
                        <!-- Vue data binding for total products -->
                        <p class="card-text larger-text" id="totalProducts">{{totalProducts}}</p> <!-- Example data -->
                    </div>
                </div>
            </div>
            <div class="col-sm-4">
                <div class="card h-100">
                    <div class="card-body d-flex flex-column justify-content-between">
                        <h5 class="card-title">Total Categories</h5>
                        <!-- Vue data binding for total categories -->
                        <p class="card-text larger-text" id="totalCategories">{{totalCategories}}</p> <!-- Example data -->
                    </div>
                </div>
            </div>
            <div class="col-sm-4">
                <div class="card h-100">
                    <div class="card-body d-flex flex-column justify-content-between">
                        <h5 class="card-title">Number of Orders Today</h5>
                        <!-- Vue data binding for orders today -->
                        <p class="card-text larger-text" id="ordersToday">{{ordersToday}}</p> <!-- Example data -->
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<style>
.larger-text {
    font-size: 2.5em; /* Adjust the size as needed */
}
</style>
<script>

import apiRequest from "@/api";
export default {
 name: "adminDashboard" ,
 data() {
    return {

        ordersToday:0,

    }
 },
 computed: {
    totalProducts(){
        return Object.keys(this.$store.state.productMaster).length
    },
    totalCategories(){
        return Object.keys(this.$store.state.categoryMaster).length
    },
 },
 async created() {
    // fetch dashboard data from api
    const userData = { username: this.$store.state.user.username };
    try {
      const responseData = await apiRequest(
        "api/admin/dashboard?username=" +
          encodeURIComponent(this.$store.state.user.username),
        "GET",
        userData,
        true
      );
      this.ordersToday = responseData.noOfOrdersToday;
    } catch (error) {
      console.log(error);
    }
  },
}
</script>
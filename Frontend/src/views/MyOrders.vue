<template>
  <div class="container" style="margin-top: 60px">
    <h3>My Orders</h3>
    <table class="table table-striped">
      <thead>
        <tr style="background-color: yellowgreen; color: white">
          <th>Order ID</th>
          <th>Number of Items</th>
          <th>Order Time</th>
          <th>Address</th>
          <th>Status</th>
          <th>Total Price</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="order in orders" :key="order.order_id">
          <tr @click="toggleRow(order)" class="clickable-row">
            <td>{{ order.order_id }}</td>
            <td>{{ Number(order.total_qty) }}</td>
            <td>{{ order.created_at }}</td>
            <td>{{ order.address }}</td>
            <td>{{ order.status }}</td>
            <td>{{ Number(order.total_price).toFixed(2) }}</td>
          </tr>
          <tr v-if="order.showDetails">
            <td colspan="6">
              <table class="table">
                <thead>
                  <tr style="background-color: burlywood">
                    <th>Item ID</th>
                    <th>Name</th>
                    <th>Quantity</th>
                    <th>Price Per Unit</th>
                    <th>Total Price</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in order.itemList" :key="item.item_id">
                    <td>{{ item.item_id }}</td>
                    <td>{{ item.name }}</td>
                    <td>{{ Number(item.qty) }}</td>
                    <td>{{ Number(item.price_per_unit) }}</td>
                    <td>{{ Number(item.total_price) }}</td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
import apiRequest from "@/api";

export default {
  name: "myOrders",
  data() {
    return {
      orders: [],
    };
  },
  methods: {
    async toggleRow(order) {
      // Toggle the showDetails property to show/hide inner rows
      order.showDetails = !order.showDetails;
    },
  },
  async created() {
    //////////////////////
    // fetch user basket data from api
    const userData = { username: this.$store.state.user.username };
    try {
      const responseData = await apiRequest(
        "api/order?username=" +
          encodeURIComponent(this.$store.state.user.username),
        "GET",
        userData,
        true
      );
      if (responseData.code == "S" || responseData.code == "ND") {
        // Add showDetails property to each order
        this.orders = responseData.orders.map((order) => {
          return { ...order, showDetails: false };
        });
        //this.basket = this.$store.state.user.basket;
      }
    } catch (error) {
      console.log(error);
    }
  },
};
</script>

<style>
tr.clickable-row:hover {
  cursor: pointer;
}
</style>

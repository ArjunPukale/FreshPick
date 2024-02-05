<template>
  <div class="container">
    <div v-if="Object.keys(this.basket).length < 1">
      <h1 style="margin-top: 100px">Basket is empty :(</h1>
    </div>

    <div v-else>
      <h1 style="margin-top: 50px">My Basket</h1>
      <table class="table">
        <thead>
          <tr>
            <th>Product</th>
            <th>Image</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>Total</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <!-- Populate basket items-->

          <tr v-for="(quantity, productId) in this.basket" :key="productId">
            <td>
              {{ getProduct(productId).name }}
            </td>
            <td>
              <img
                :src="
                  this.$store.state.imageEndpoint +
                  getProduct(productId).product_img
                "
                class=""
                :alt="getProduct(productId).name"
                width="50"
                height="50"
              />
            </td>
            <td>
              <span class="original-price"
                >&#x20B9;{{
                  Number(getProduct(productId).product_price_per_unit).toFixed(
                    2
                  )
                }}</span
              >
              <span>
                &#x20B9;{{
                  getDiscountedPrice(
                    Number(getProduct(productId).product_price_per_unit),
                    getProduct(productId).product_discount
                  )
                }}</span
              >
            </td>
            <td>
              <input
                type="number"
                min="1"
                v-model="basket[productId]"
                @change="handleQtyChange"
                class="form-control quantity-input"
              />
            </td>
            <td class="total-price">
              &#x20B9;{{
                Number(
                  getDiscountedPrice(
                    Number(getProduct(productId).product_price_per_unit),
                    getProduct(productId).product_discount
                  ) * quantity
                ).toFixed(2)
              }}
            </td>

            <td>
              <button
                @click="removeBasketItem(productId)"
                class="btn btn-danger btn-sm remove-btn"
              >
                Remove
              </button>
            </td>
          </tr>

          <!-- Populate basket items ends-->
        </tbody>
        <tfoot>
          <tr>
            <td colspan="4" align="right"><strong>Total Price:</strong></td>
            <td class="grand-total" colspan="2">
              <strong>&#x20B9;{{ totalPrice.toFixed(2) }}</strong>
            </td>
          </tr>
          <tr>
            <td colspan="4" align="right"><strong>Total Discount:</strong></td>
            <td class="total-discount" colspan="2">
              <strong>&#x20B9;{{ totalDiscount.toFixed(2) }}</strong>
            </td>
          </tr>
          <tr>
            <td colspan="6" align="right">
              <button
                @click="saveCart(false)"
                :disabled="!saveCartButton"
                class="btn btn-primary"
                id="saveBasket"
              >
                Save Cart
              </button>

              <button
                class="btn btn-success"
                style="margin-left: 15px"
                @click="saveCart(true)"
              >
                Place Order
              </button>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "BasketView",
  data() {
    return {
      //basket: {},
      //products: null,
      saveCartButton: false,
    };
  },
  async created() {
    //////////////////////
    // fetch user basket data from api
    const userData = { username: this.$store.state.user.username };
    try {
      const responseData = await apiRequest(
        "api/basket?username=" +
          encodeURIComponent(this.$store.state.user.username),
        "GET",
        userData,
        true
      );
      if (responseData.code == "S" || responseData.code == "ND") {
        this.$store.commit("setUserBasket", responseData.basket);
        //this.basket = this.$store.state.user.basket;
      }
    } catch (error) {
      console.log(error);
    }
  },

  methods: {
    getDiscountedPrice(ogPrice, discount) {
      let discPrice = (ogPrice * (100 - discount)) / 100;
      return discPrice.toFixed(2);
    },
    getProduct(productId) {
      return this.products[productId] || {}; // Return an empty object if the product doesn't exist
    },
    handleQtyChange() {
      this.saveCartButton = true;
    },
    async removeBasketItem(productId) {
      //send api request to delete basket item

      try {
        const userData = { username: this.$store.state.user.username };
        const responseData = await apiRequest(
          "api/basket?username=" +
            encodeURIComponent(this.$store.state.user.username) +
            "&id=" +
            productId,
          "DELETE",
          userData,
          true
        );
        if (responseData.code == "S") {
          alert("Item deleted successfully !");
          this.$store.commit("setUserBasket", responseData.basket);
          // this.basket = this.$store.state.user.basket;
        } else if (responseData.code == "ND") {
          alert("Item not present in your basket !");
          this.$store.commit("setUserBasket", responseData.basket);
          // this.basket = this.$store.state.user.basket;
        } else {
          alert("Something went wrong !");
        }
      } catch (error) {
        console.log(error);
        alert("Error");
      }
    },

    async saveCart(placeOrder) {
      //send api request to save the user's basket
      const userData = {
        username: this.$store.state.user.username,
        basket: this.basket,
      };

      try {
        const responseData = await apiRequest(
          "api/basket",
          "PUT",
          userData,
          true
        );
        if (responseData.status) {
          let allItemsSaved = true;
          for (const productId in responseData.status) {
            const status = responseData.status[productId];
            if (status == "O") {
              allItemsSaved = false;
              let name = this.products[productId].name;
              let availQty = responseData.OOS[productId];
              alert(
                "selected qty for " +
                  name +
                  " is more than available stock : " +
                  availQty
              );
            }
          }

          this.$store.commit("setUserBasket", responseData.basket);
          this.saveCartButton = false;

          if (allItemsSaved) {
            if (placeOrder) {
              this.$router.push("/orderConfirmation");
            } else {
              //save cart
              alert("basket saved !");
            }
          }
        }
      } catch (error) {
        console.log(error);
      }
    },
  },
  computed: {
    basket() {
      return this.$store.state.user.basket;
    },
    products() {
      return this.$store.state.productMaster;
    },
    totalPrice() {
      let totalPrice = 0;
      for (const productId in this.basket) {
        if (this.products[productId]) {
          totalPrice +=
            this.getDiscountedPrice(
              Number(this.products[productId].product_price_per_unit),
              this.products[productId].product_discount
            ) * this.basket[productId];
        }
      }
      return totalPrice;
    },
    totalDiscount() {
      let totalDiscount = 0;
      for (const productId in this.basket) {
        if (this.products[productId]) {
          totalDiscount += Number(
            (this.products[productId].product_price_per_unit *
              this.products[productId].product_discount *
              this.basket[productId]) /
              100
          );
        }
      }
      console.log(totalDiscount);
      return totalDiscount;
    },
  },
};
</script>

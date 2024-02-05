<template>
  <div class="container">
    <h1 style="margin-top: 50px">Order Confirmation</h1>

    <table>
      <thead>
        <tr>
          <th scope="col">Product Name</th>
          <th scope="col">Quantity</th>
          <th scope="col">Price</th>
          <th scope="col">Total Price</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(quantity, productId) in this.basket" :key="productId">
          <td>
            {{ getProduct(productId).name }}
          </td>
          <td class="quantity">{{ basket[productId] }}</td>
          <td>
            <span class="original-price"
              >&#x20B9;{{
                Number(getProduct(productId).product_price_per_unit).toFixed(2)
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
            &#x20B9;{{
              Number(
                getDiscountedPrice(
                  Number(getProduct(productId).product_price_per_unit),
                  getProduct(productId).product_discount
                ) * quantity
              ).toFixed(2)
            }}
          </td>
        </tr>
      </tbody>
    </table>

    <div class="row">
      <div class="col-md-6">
        <h4>Total Amount: &#x20B9;{{ totalPrice.toFixed(2) }}</h4>
      </div>
    </div>
    <div class="row">
      <div class="col-md-6">
        <h4>Total Discount: &#x20B9;{{ totalDiscount.toFixed(2) }}</h4>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-md-6">
        <h4>Delivery Address</h4>

        <div class="mb-3">
          <label for="address" class="form-label">Address</label>
          <textarea
            class="form-control address-input"
            id="address"
            name="address"
            rows="4"
            v-model="address"
            required
          >
          </textarea>
        </div>
        <div class="mb-3">
          <label for="contact" class="form-label">Contact No.</label>
          <input
            type="text"
            class="form-control"
            id="contact"
            name="contact"
            required
            v-model="phoneNumber"
            @input="validatePhoneNumber"
          />
          <!-- <div class="invalid-feedback">
            Please enter a valid contact number.
          </div> -->
          <p
            :class="{
              'valid-phone': phoneNumberIsValid,
              'invalid-phone': !phoneNumberIsValid,
            }"
          >
            {{
              phoneNumberIsValid
                ? "Phone number is valid!"
                : "Phone number is invalid! Please enter a 10-digit number."
            }}
          </p>
        </div>
        <button
          @click="placeOrder"
          type="submit"
          class="btn btn-primary"
          id="placeOrderConfirm"
        >
          Place Order
        </button>
      </div>
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "orderConfirmation",
  data() {
    return {
      address: this.$store.state.user.address,
      phoneNumber: this.$store.state.user.phoneNumber,
      phoneNumberIsValid:
        this.$store.state.user.phoneNumber.length == 10 ? true : false,
    };
  },
  methods: {
    getDiscountedPrice(ogPrice, discount) {
      let discPrice = (ogPrice * (100 - discount)) / 100;
      return discPrice.toFixed(2);
    },
    getProduct(productId) {
      return this.products[productId] || {}; // Return an empty object if the product doesn't exist
    },
    validatePhoneNumber() {
      // Implement your custom validation logic here
      // Custom validation logic for a 10-digit number
      this.phoneNumber = this.phoneNumber.replace(/\D/g, ""); // Remove non-digits
      this.phoneNumberIsValid = this.phoneNumber.length === 10;
    },
    async placeOrder() {
      // send api request to place order
      const userData = {
        username: this.$store.state.user.username,
        basket: this.basket,
        address: this.address,
        contact: this.phoneNumber,
      };
      try {
        const responseData = await apiRequest(
          "api/order",
          "POST",
          userData,
          true
        );
        if (responseData.code == "S") {
          alert(
            "order placed successfully , order id: " + responseData.orderId
          );
          this.$router.push("/orders");
        } else if (responseData.code == "PS") {
          alert("Partial success");
          for (const productId in responseData.OOS) {
            const availQty = responseData.OOS[productId];
            const name = this.getProduct(productId).name;
            alert(
              "selected qty for " +
                name +
                " is more than available stock : " +
                availQty
            );
          }
          this.$router.push("/orders");
        } else {
          alert("Order placement failed");
          this.$router.push("/basket");
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
<style scoped>
table {
  border: 1px solid #ccc;
  border-collapse: collapse;
  width: 100%;
}

th,
td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #ccc;
}

tbody tr:last-child td {
  border-bottom: none;
}
.valid-phone {
  color: green;
}

.invalid-phone {
  color: red;
}
.address-input {
  height: 120px;
  resize: none;
}
.original-price {
  text-decoration: line-through;
}
</style>

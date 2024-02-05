<template>
  <div class="col-md-3 card-equal-height">
    <div class="card">
      <img
        :src="this.$store.state.imageEndpoint + this.product.product_img"
        class="card-img-top"
        :alt="this.product.name"
      />
      <div class="discount-label">{{ this.product.product_discount }}% off</div>
      <div class="card-body">
        <h5 class="card-title">{{ this.product.name }}</h5>

        <span v-if="this.product.veg_nveg == 'V'" class="badge bg-success"
          >Veg</span
        >

        <span v-else class="badge bg-danger">NonVeg</span>

        <p class="card-text">
          {{ this.product.product_desc.slice(0, 40) + "..." }}
        </p>
        <p>
          <span class="original-price"
            >&#x20B9;{{
              Number(this.product.product_price_per_unit).toFixed(2)
            }}</span
          >
          <span class="discounted-price"
            >&#x20B9;{{
              getDiscountedPrice(
                Number(this.product.product_price_per_unit),
                this.product.product_discount
              )
            }}</span
          >
          <span class="product-unit"> per {{ this.product.product_unit }}</span>
          <!-- <span class="discounted-label">(25% off)</span> -->
        </p>

        <!-- Replace 'bg-success' with 'bg-danger' for Non-Veg -->
        <div class="input-group mb-3">
          <div class="input-group-prepend">
            <button
              @click="decQty"
              class="btn btn-outline-primary minusBtn"
              type="button"
            >
              -
            </button>
          </div>
          <input
            type="text"
            class="form-control quantityInput"
            v-model="qty"
            readonly
          />
          <div class="input-group-append">
            <button
              @click="incQty"
              class="btn btn-outline-primary plusBtn"
              type="button"
            >
              +
            </button>
          </div>
        </div>

        <button
          v-if="this.product.product_stock > 0"
          @click="addToBasket"
          class="btn btn-primary addToBasketBtn"
        >
          Add to Basket
        </button>

        <button v-else class="btn btn-secondary" disabled>Not Available</button>
      </div>
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "product-card",
  props: ["product", "productId"],
  data() {
    return {
      qty: 1,
    };
  },
  methods: {
    getDiscountedPrice(ogPrice, discount) {
      let discPrice = (ogPrice * (100 - discount)) / 100;
      return discPrice.toFixed(2);
    },
    incQty() {
      this.qty += 1;
    },
    decQty() {
      if (this.qty > 1) {
        this.qty -= 1;
      }
    },
    async addToBasket() {
      //send api request to add item in basket
      const userData = {
        username: this.$store.state.user.username,
        item: {
          productId: this.productId,
          qty: this.qty,
        },
      };
      try {
        const responseData = await apiRequest(
          "api/basket",
          "POST",
          userData,
          true
        );
        if (responseData.code == "S") {
          alert("Item added to your basket successfully !");
          this.$store.commit("setUserBasket", responseData.basket);
        } else if (responseData.code == "D") {
          alert("Item already present in your basket !");
          this.$store.commit("setUserBasket", responseData.basket);
        } else {
          alert("Something went wrong !");
        }
      } catch (error) {
        console.log(error);
        alert("Error");
      }
    },
  },
};
</script>
<style>
/* .card {
  margin-bottom: 20px;
  width: auto;
} */
.card-body {
  font-size: small;
}
.card-img-top {
  height: 120px;
}
.original-price {
  text-decoration: line-through;
}
.discount-label {
  position: absolute;
  top: 5; /* Adjust the top and right values for positioning */
  right: 5;
  background-color: #127418; /* Adjust the background color of the label */
  color: #ffffff; /* Adjust the text color of the label */
  padding: 3px 5px; /* Adjust the padding as needed */
  font-weight: bold;
}

.card-container {
  /* display: flex; */
  flex-wrap: wrap;
  margin-left: 50px;
  margin-right: 50px;
}

.card-equal-height {
  display: flex;
  max-width: fit-content;
}

.card {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  width: 200px;
}
</style>

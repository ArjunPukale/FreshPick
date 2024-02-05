<template>
  <div class="card-container">
    <h6 class="display-3">{{ this.category.name.toUpperCase() }}</h6>

    <div class="row">
      <productCard
        v-for="productId in this.category.products"
        :key="productId"
        :product="this.products[productId]"
      />
    </div>
    <div class="row mt-3">
      <div class="col-md-12 text-center">
        <a @click="goToHome()" class="btn btn-outline-success">Back</a>
      </div>
    </div>
    <hr class="hr hr-blurry" />
  </div>
</template>
<script>
import productCard from "@/components/product-card.vue";
export default {
  name: "product-display-home",
  components: {
    productCard,
  },
  props: ["specifiedCatId", "allCategoryDisplay"],
  data() {
    return {
      category: null,
      products: null,
    };
  },
  methods: {
    goToHome() {
      this.allCategoryDisplay();
    },
  },
  computed: {},
  created() {
    this.category = this.$store.state.categoryMaster[this.specifiedCatId];
    this.products = this.$store.state.productMaster;
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

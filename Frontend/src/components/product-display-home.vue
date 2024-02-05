<template>
  <div
    v-for="(category, categoryId) in displayCategories"
    :key="categoryId"
    class="card-container"
  >
    <h6 class="display-6">{{ category.name.toUpperCase() }}</h6>

    <div class="row">
      <productCard
        v-for="productId in category.products"
        :key="productId"
        :product="this.products[productId]"
        :productId="productId"
      />
    </div>
    <div class="row mt-3">
      <div class="col-md-12 text-center">
        <a
          v-on:click="this.categoryDisplay(categoryId)"
          class="btn btn-outline-success"
          >View More</a
        >
      </div>
    </div>
    <hr class="hr hr-blurry" />
  </div>
</template>
<script>
import apiRequest from "@/api";
import productCard from "@/components/product-card.vue";
export default {
  name: "product-display-home",
  components: {
    productCard,
  },
  props: ["categoryDisplay"],
  data() {
    return {
      categories: null,
      products: null,
    };
  },
  methods: {},
  computed: {
    displayCategories() {
      // Computed property that doubles the originalValue
      // Filter the products arrays in each category to keep only the first 9 elements
      const filteredCategories = {};

      for (const categoryId in this.categories) {
        const category = this.categories[categoryId];
        const filteredProducts = category.products.slice(0, 9); // Get the first 9 elements
        filteredCategories[categoryId] = {
          ...category,
          products: filteredProducts,
        };
      }
      return filteredCategories;
    },
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

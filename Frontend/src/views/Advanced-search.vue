<template>
  <searchBarAdvanced
    :queryStr="productName"
    :updateProductList="updateProductList"
  />
  <div v-if="productList" class="card-container">
    <h6>Search results for '{{ pName ? pName : productName }}'</h6>
    <div class="row">
      <productCard
        v-for="productId in productList"
        :key="productId"
        :product="this.products[productId]"
        :productId="productId"
      />
    </div>
  </div>
  <div v-else class="card-container">
    <h6>No results found for '{{ pName ? pName : productName }}'</h6>
  </div>
</template>
<script>
import searchBarAdvanced from "@/components/search-bar-advanced.vue";
import productCard from "@/components/product-card.vue";
export default {
  name: "advancedSearch",
  components: {
    searchBarAdvanced,
    productCard,
  },
  data() {
    return {
      minDiscount: 0,
      minPrice: 0,
      maxPrice: 1000,
      productList: null,
      products: null,
      pName: null,
    };
  },
  computed: {
    productName() {
      return this.$route.params.queryStr;
    },
  },
  methods: {
    updatePriceRange() {
      // Ensure minPrice is not greater than maxPrice
      if (this.minPrice > this.maxPrice) {
        this.minPrice = this.maxPrice;
      }
    },
    updateProductList(pList, queryStr) {
      this.productList = pList;
      this.pName = queryStr;
      console.log(
        "inside updateProductList :: productList:: " + this.productList
      );
    },
  },
  created() {
    this.products = this.$store.state.productMaster;
  },
  mounted() {
    // this.productName = this.$route.params.queryStr;
    // console.log(this.productName);
  },
};
</script>

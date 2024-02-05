<template>
  <div class="container">
    <div class="col-md-12">
      <div class="search-container">
        <label for="search" class="sr-only">Search for products</label>
        <input
          type="text"
          id="search"
          class="form-control search-box"
          placeholder="Search for products"
          v-model="productName"
        />
        <button @click="searchProducts" class="btn btn-primary" type="button">
          Search
        </button>
      </div>
    </div>
  </div>
</template>
<style>
.search-container {
  display: flex;
  text-align: center;
  padding: 20px;
}
.search-box {
  width: 70%;
}
</style>
<script>
export default {
  name: "search-bar-basic",
  data() {
    return {
      productName: "",
    };
  },
  methods: {
    searchProducts() {
      console.log(this.productName);
      this.$router.push({
        name: "searchProduct",
        params: { queryStr: this.productName },
      });
    },
  },
};
</script>

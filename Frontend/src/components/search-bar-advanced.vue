<template>
  <div class="row justify-content-md-center" style="margin-top: 60px">
    <div class="col-6">
      <div class="form-row align-items-center">
        <div class="col-auto">
          <select
            v-model="selectedCategory"
            class="form-control mb-2"
            name="category"
          >
            <option value="">All Categories</option>

            <option
              v-for="(category, categoryId) in categories"
              :key="categoryId"
              :value="categoryId"
            >
              {{ category.name }}
            </option>
          </select>
        </div>
        <div class="col">
          <input
            type="text"
            class="form-control mb-2"
            name="query"
            placeholder="Search for products"
            v-model="product_name"
          />
        </div>
        <div class="col-auto">
          <button
            @click="searchProducts"
            type="submit"
            class="btn btn-primary mb-2"
          >
            Search
          </button>
        </div>
      </div>

      <button
        type="button"
        class="btn btn-primary mt-3"
        @click="toggleAdvanceFilter"
      >
        {{
          showAdvanceFilter ? "Hide Advanced Filter" : "Show Advanced Filter"
        }}
      </button>
      <div v-if="showAdvanceFilter" id="filterPanel" class="mt-3">
        <div class="card card-body" style="width: auto">
          <div class="form-group">
            <div class="row">
              <div class="col-3">
                <label for="minPrice">Min Price:</label>
                <input
                  type="number"
                  id="minPrice"
                  v-model="minPrice"
                  @input="updatePriceRange"
                />
              </div>
              <div class="col-2">
                <label for="maxPrice">Max Price:</label>
                <input
                  type="number"
                  id="maxPrice"
                  v-model="maxPrice"
                  @input="updatePriceRange"
                />
              </div>
            </div>
          </div>
          <div class="form-group">
            <div class="row">
              <div class="col-2">
                <label for="minDiscountInput">Min Discount:</label>
              </div>
              <div class="col-2">
                <input
                  readonly
                  type="number"
                  class="form-control"
                  id="minDiscountInput"
                  placeholder="0"
                  min="0"
                  max="100"
                  v-model="minDiscount"
                />
              </div>
              <div class="col-3">
                <input
                  type="range"
                  class="custom-range"
                  id="minDiscountRange"
                  min="0"
                  max="100"
                  v-model="minDiscount"
                />
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Vegetarian/Non-Vegetarian:</label><br />
            <div class="form-check form-check-inline">
              <input
                type="radio"
                id="vegRadio"
                value="V"
                v-model="v_nv_option"
              />
              <label class="form-check-label" for="veg">Vegetarian</label>
            </div>
            <div class="form-check form-check-inline">
              <input
                type="radio"
                id="nonVegRadio"
                value="NV"
                v-model="v_nv_option"
              />
              <label class="form-check-label" for="nonVeg"
                >Non-Vegetarian</label
              >
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<style></style>
<script>
import apiRequest from "@/api";
export default {
  name: "search-bar-advanced",
  props: ["queryStr", "updateProductList"],
  data() {
    return {
      product_name: "",
      minDiscount: 0,
      minPrice: 0,
      maxPrice: 1000,
      v_nv_option: "V",
      selectedCategory: "",
      productList: [],
      products: this.$store.state.productMaster,
      categories: this.$store.state.categoryMaster,
      showAdvanceFilter: false,
    };
  },
  async mounted() {
    this.product_name = this.queryStr;
    if (this.product_name && this.product_name != "") {
      //api call to fetch products with name like this
      try {
        const userData = {
          username: this.$store.state.user.username,
          query: this.product_name,
        };
        const responseData = await apiRequest(
          "api/search",
          "POST",
          userData,
          true
        );
        if (responseData.code == "S") {
          this.productList = responseData.productList;
          this.updateProductList(this.productList, this.queryStr);
        } else {
          this.productList = null;
          this.updateProductList(this.productList, this.product_name);
        }
      } catch (error) {
        console.log(error);
      }
    }
  },
  methods: {
    toggleAdvanceFilter() {
      this.showAdvanceFilter = !this.showAdvanceFilter;
    },
    updatePriceRange() {
      // Ensure minPrice is not greater than maxPrice
      if (this.minPrice > this.maxPrice) {
        this.minPrice = this.maxPrice;
      }
    },
    async searchProducts() {
      if (this.product_name && this.product_name != "") {
        //api call to fetch products with name like this
        try {
          const userData = {
            username: this.$store.state.user.username,
            query: this.product_name,
            minDiscountValue: this.minDiscount,
            vegNonveg: this.v_nv_option,
            minPrice: this.minPrice,
            maxPrice: this.maxPrice,
            categoryId: this.selectedCategory,
          };
          const responseData = await apiRequest(
            "api/search",
            "POST",
            userData,
            true
          );
          if (responseData.code == "S") {
            this.productList = responseData.productList;
            this.updateProductList(this.productList, this.product_name);
          } else {
            this.productList = null;
            this.updateProductList(this.productList, this.product_name);
          }
        } catch (error) {
          console.log(error);
        }
      }
    },
  },
};
</script>

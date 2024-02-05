<template>
  <div class="container mt-4">
    <h2 style="margin-top: 60px">Product Management</h2>

    <router-link to="/admin/product/add" class="btn btn-primary mb-2"
      >Add New Product</router-link
    >
    <!-- Search Bar -->

    <div>
      <div class="search-container">
        <label for="search" class="sr-only">Search for products</label>
        <input
          type="text"
          class="form-control search-box"
          placeholder="Search for categories"
          v-model="search_query"
        />
        <button @click="searchProducts" class="btn btn-primary" type="button">
          Search
        </button>
      </div>
    </div>

    <!-- Table -->
    <!-- Table -->
    <div class="table-wrapper">
      <table class="table table-bordered">
        <thead style="background-color: burlywood">
          <tr>
            <th>Product ID</th>
            <th>Name</th>
            <th>Image</th>
            <th>Category</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(product, productId) in products" :key="productId">
            <td>{{ productId }}</td>
            <td>{{ product.name }}</td>
            <td>
              <img
                :src="this.$store.state.imageEndpoint + product.product_img"
                :alt="product.name"
                style="max-height: 50px"
              />
            </td>
            <td>{{ categories[product.category_id].name }}</td>
            <td>
              &#x20B9;{{ Number(product.product_price_per_unit).toFixed(2) }}
            </td>
            <td>
              {{ Number(product.product_stock) }} {{ product.product_unit }}
            </td>
            <td>
              <router-link
                :to="{
                  name: 'editProduct',
                  params: { productId: productId },
                }"
                class="btn btn-primary btn-sm"
                >Edit</router-link
              >
              <button
                @click="deleteProduct(productId)"
                class="btn btn-danger btn-sm"
              >
                Delete
              </button>
            </td>
          </tr>

          <!-- Add more rows for other products here -->
        </tbody>
      </table>
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "product-management",
  data() {
    return {
      categories: null,
      //products: null,
      search_query: "",
    };
  },
  computed: {
    products() {
      return this.$store.state.productMaster;
    },
  },
  created() {
    this.categories = this.$store.state.categoryMaster;
    //this.products = this.$store.state.productMaster;
  },
  methods: {
    searchProducts() {
      const filteredProducts = Object.keys(this.$store.state.productMaster)
        .filter((productId) =>
          this.$store.state.productMaster[productId].name
            .toLowerCase()
            .includes(this.search_query.toLowerCase())
        )
        .reduce((result, productId) => {
          result[productId] = this.$store.state.productMaster[productId];
          return result;
        }, {});
      this.products = filteredProducts;
    },
    async deleteProduct(productId) {
      const confirmation = confirm("Do you want to delete this product ?");
      if (confirmation) {
        try {
          const userData = { username: this.$store.state.user.username };
          const responseData = await apiRequest(
            "api/admin/product?username=" +
              encodeURIComponent(this.$store.state.user.username) +
              "&id=" +
              productId,
            "DELETE",
            userData,
            true
          );
          if (responseData.code == "S") {
            alert("Product deleted successfully");
            this.$store.commit("setCategoryMaster", responseData.categories);
            this.$store.commit("setProductMaster", responseData.products);
            this.$router.push("/admin/productManagement");
          } else if (responseData.code == "ND") {
            this.error = true;
            this.message = "No such product exists !";
          } else {
            this.error = true;
            this.message = "Something went wrong !";
          }
        } catch (error) {
          // Handle errors
          console.log(error);
          this.error = true;
          this.message = "Failure !";
        }
      }
    },
  },
};
</script>

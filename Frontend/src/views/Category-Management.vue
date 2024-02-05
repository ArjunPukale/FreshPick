<template>
  <div class="container mt-4">
    <h2 style="margin-top: 60px">Category Management</h2>
    <!-- Add New Category Button -->
    <router-link to="/admin/category/add" class="btn btn-primary mb-2"
      >Add New Category</router-link
    >
    <!-- Search Bar -->

    <div>
      <div class="search-container">
        <label for="search" class="sr-only">Search for categories</label>
        <input
          type="text"
          class="form-control search-box"
          placeholder="Search for categories"
          v-model="search_query"
        />
        <button @click="searchCategories" class="btn btn-primary" type="button">
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
            <th>Category ID</th>
            <th>Category Name</th>
            <th># Products</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(category, categoryId) in categories" :key="categoryId">
            <td>{{ categoryId }}</td>
            <td>{{ category.name.toUpperCase() }}</td>
            <td>{{ category.products.length }}</td>

            <td>
              <router-link
                :to="{
                  name: 'editCategory',
                  params: { categoryId: categoryId },
                }"
                class="btn btn-primary btn-sm"
                >Edit</router-link
              >
              <button
                @click="deleteCategory(categoryId)"
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
<style>
.search-container {
  padding-left: 0px;
}
</style>
<script>
import apiRequest from "@/api";
export default {
  name: "category-management",
  data() {
    return {
      //categories: null,
      //products: null,
      search_query: "",
    };
  },
  computed: {
    products() {
      return this.$store.state.productMaster;
    },
    categories() {
      return this.$store.state.categoryMaster;
    },
  },
  created() {
    // this.categories = this.$store.state.categoryMaster;
    // this.products = this.$store.state.productMaster;
  },
  methods: {
    searchCategories() {
      const filteredCategories = Object.keys(this.$store.state.categoryMaster)
        .filter((categoryId) =>
          this.$store.state.categoryMaster[categoryId].name
            .toLowerCase()
            .includes(this.search_query.toLowerCase())
        )
        .reduce((result, categoryId) => {
          result[categoryId] = this.$store.state.categoryMaster[categoryId];
          return result;
        }, {});
      this.categories = filteredCategories;
    },
    async deleteCategory(categoryId) {
      const confirmation = confirm("Do you want to delete this category ?");
      if (confirmation) {
        try {
          const userData = { username: this.$store.state.user.username };
          const responseData = await apiRequest(
            "api/admin/category?username=" +
              encodeURIComponent(this.$store.state.user.username) +
              "&id=" +
              categoryId,
            "DELETE",
            userData,
            true
          );
          if (responseData.code == "S") {
            alert("category deleted successfully");
            this.$store.commit("setCategoryMaster", responseData.categories);
            this.$store.commit("setProductMaster", responseData.products);
            this.$router.push("/admin/categoryManagement");
          } else if (responseData.code == "ND") {
            this.error = true;
            this.message = "No such category exists !";
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

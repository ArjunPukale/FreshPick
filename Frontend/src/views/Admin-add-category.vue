<template>
  <div class="container" style="margin-top: 100px">
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ message }}
    </div>
    <h2>Add Category</h2>

    <div class="form-group">
      <label for="product-name">Category Name</label>
      <input
        type="text"
        class="form-control"
        name="category-name"
        placeholder="Enter category name"
        v-model="category_name"
        required
      />
    </div>

    <button @click="addCategory" type="submit" class="btn btn-primary">
      Add Category
    </button>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "add-category",
  data() {
    return {
      category_name: "",
      error: false,
      message: "",
    };
  },
  methods: {
    async addCategory() {
      //send api request to add a new category
      const userData = {
        username: this.$store.state.user.username,
        categoryName: this.category_name,
      };

      try {
        const responseData = await apiRequest(
          "api/admin/category",
          "POST",
          userData,
          true
        );
        if (responseData.code == "S") {
          alert("Category added successfully");
          this.$store.commit("setCategoryMaster", responseData.categories);
          this.$router.push("/admin/categoryManagement");
        } else if (responseData.code == "D") {
          this.error = true;
          this.message = "Category with same name already exists !";
        } else {
          this.error = true;
          this.message = "Something went wrong !";
        }
      } catch (error) {
        console.log(error);
        this.error = true;
        this.message = "Failure !";
      }
    },
  },
};
</script>

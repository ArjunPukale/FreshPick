<template>
  <div class="container" style="margin-top: 100px">
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ message }}
    </div>
    <h2>Edit Category</h2>
    <div style="margin-bottom: 100px">
      <div class="form-group">
        <label for="category-name">Category Name</label>
        <input
          type="text"
          class="form-control"
          id="category-name"
          v-model="category.name"
          name="category-name"
          placeholder="Enter category name"
          required
        />
      </div>

      <button @click="editCategory" type="submit" class="btn btn-primary">
        Save Category
      </button>
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "edit-category",
  props: {
    categoryId: {
      type: String, // Adjust the type based on your needs (String, Number, etc.)
      required: true,
    },
  },
  data() {
    return {
      category: null,
    };
  },
  created() {
    this.category = this.$store.state.categoryMaster[this.categoryId];
  },
  methods: {
    async editCategory() {
      //send api request to edit the category
      const userData = {
        username: this.$store.state.user.username,
        categoryName: this.category.name,
        categoryId: this.categoryId,
      };
      try {
        const responseData = await apiRequest(
          "api/admin/category",
          "PUT",
          userData,
          true
        );
        if (responseData.code == "S") {
          alert("Category saved successfully");
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

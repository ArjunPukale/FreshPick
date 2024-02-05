<template>
  <div class="container" style="margin-top: 100px">
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ message }}
    </div>
    <h2>Add Product</h2>
    <div style="margin-bottom: 100px">
      <div class="form-group">
        <label for="product-name">Product Name</label>
        <input
          type="text"
          class="form-control"
          v-model="product_name"
          name="product-name"
          placeholder="Enter product name"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-description">Product Description</label>
        <textarea
          class="form-control"
          v-model="product_description"
          name="product-description"
          rows="3"
          placeholder="Enter product description"
          required
        ></textarea>
      </div>
      <div class="form-group">
        <label for="product-price">Product Price</label>
        <input
          type="number"
          class="form-control"
          v-model="product_price"
          name="product-price"
          placeholder="Enter product price"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-quantity">Product Quantity</label>
        <input
          type="number"
          class="form-control"
          v-model="product_quantity"
          name="product-quantity"
          placeholder="Enter product quantity"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-category">Product Category</label>
        <select
          class="form-control"
          v-model="selectedCategory"
          name="product-category"
          required
        >
          <option value="">Select category</option>
          <option
            v-for="(category, categoryId) in categories"
            :key="categoryId"
            :value="categoryId"
          >
            {{ category.name }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label for="product-type">Product Type</label>
        <select
          class="form-control"
          v-model="selectedProductType"
          name="product-type"
          required
        >
          <option value="">Select type</option>
          <option value="V">Vegetarian</option>
          <option value="NV">Non-Vegetarian</option>
        </select>
      </div>
      <div class="form-group">
        <label for="product-unit">Product Unit</label>
        <select
          class="form-control"
          v-model="selectedProductUnit"
          name="product-unit"
          required
        >
          <option value="">Select unit</option>
          <option value="kg">kg</option>
          <option value="ltr">ltr</option>
          <option value="unit">unit</option>
        </select>
      </div>
      <div class="form-group">
        <label for="product-discount">Product Discount</label>
        <input
          type="number"
          class="form-control"
          v-model="product_discount"
          name="product-discount"
          placeholder="Enter product discount"
          min="0"
          max="100"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-manufactured-date">Manufactured Date</label>
        <input
          type="date"
          class="form-control"
          v-model="product_manufactured_date"
          name="product-manufactured-date"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-expiry-date">Expiry Date</label>
        <input
          type="date"
          class="form-control"
          v-model="product_expiry_date"
          name="product-expiry-date"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-image">Product Image (JPEG, JPG, PNG only)</label>
        <input
          type="file"
          class="form-control-file"
          id="product-image"
          name="product-image"
          accept=".jpeg, .jpg, .png"
          @change="handleImageUpload"
          required
        />
      </div>
      <button @click="addProduct" class="btn btn-primary">Add Product</button>
    </div>
  </div>
</template>
<script>
import axios from "axios";
export default {
  name: "add-product",
  data() {
    return {
      categories: null,
      category_name: "",
      error: false,
      message: "",
      product_name: "",
      product_description: "",
      product_price: "",
      product_quantity: "",
      selectedCategory: "",
      selectedProductType: "",
      selectedProductUnit: "",
      product_discount: "",
      product_manufactured_date: "",
      product_expiry_date: "",
      image: null,
    };
  },
  created() {
    this.categories = this.$store.state.categoryMaster;
  },
  methods: {
    async addProduct() {
      const formData = new FormData();
      formData.append("username", this.$store.state.user.username);
      formData.append("product-name", this.product_name);
      formData.append("product-description", this.product_description);
      formData.append("product-price", this.product_price);
      formData.append("product-quantity", this.product_quantity);
      formData.append("product-type", this.selectedProductType);
      formData.append("product-unit", this.selectedProductUnit);
      formData.append("product-discount", this.product_discount);
      formData.append("product-category", this.selectedCategory);
      formData.append(
        "product-manufactured-date",
        this.product_manufactured_date
      );
      formData.append("product-expiry-date", this.product_expiry_date);
      formData.append("product-image", this.image);
      try {
        let token = "";
        if (this.$store.state.user) {
          token = this.$store.state.user.token;
        }
        const baseUrl = this.$store.state.apiBaseUrl;
        const response = await axios.post(
          baseUrl + "api/admin/product",
          formData,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
        const responseData = response.data;
        if (responseData.code == "S") {
          alert("Product added successfully");
          this.$store.commit("setCategoryMaster", responseData.categories);
          this.$store.commit("setProductMaster", responseData.products);
          this.$router.push("/admin/productManagement");
        } else if (responseData.code == "D") {
          this.error = true;
          this.message = "Product with same name already exists !";
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
    },

    handleImageUpload(event) {
      this.image = event.target.files[0];
      console.log(event.target.files[0]);
    },
  },
};
</script>

<template>
  <div class="container" style="margin-top: 100px">
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ message }}
    </div>
    <h2>Edit Product</h2>
    <div style="margin-bottom: 100px">
      <div class="form-group">
        <label for="product-name">Product Name</label>
        <input
          type="text"
          class="form-control"
          id="product-name"
          name="product-name"
          v-model="product.name"
          placeholder="Enter product name"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-description">Product Description</label>
        <textarea
          class="form-control"
          id="product-description"
          name="product-description"
          v-model="product.product_desc"
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
          id="product-price"
          name="product-price"
          v-model="product_price"
          placeholder="Enter product price"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-quantity">Product Quantity</label>
        <input
          type="number"
          class="form-control"
          id="product-quantity"
          name="product-quantity"
          placeholder="Enter product quantity"
          v-model="product.product_stock"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-category">Product Category</label>
        <select
          class="form-control"
          id="product-category"
          name="product-category"
          v-model="selectedCategory"
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
          id="product-type"
          name="product-type"
          v-model="selectedProductType"
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
          id="product-unit"
          name="product-unit"
          v-model="selectedProductUnit"
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
          id="product-discount"
          name="product-discount"
          v-model="product.product_discount"
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
          id="product-manufactured-date"
          name="product-manufactured-date"
          v-model="product_manufactured_date"
          required
        />
      </div>
      <div class="form-group">
        <label for="product-expiry-date">Expiry Date</label>
        <input
          type="date"
          class="form-control"
          id="product-expiry-date"
          name="product-expiry-date"
          v-model="product_expiry_date"
          required
        />
      </div>
      <div class="form-group">
        <img
          :src="this.$store.state.imageEndpoint + this.product.product_img"
          :alt="this.product.name"
          style="max-height: 50px"
        />
        <label for="product-image">Product Image (JPEG, JPG, PNG only)</label>
        <input
          type="file"
          class="form-control-file"
          id="product-image"
          name="product-image"
          @change="handleImageUpload"
          accept=".jpeg, .jpg, .png"
        />
      </div>
      <button @click="editProduct" type="submit" class="btn btn-primary">
        Save Product
      </button>
    </div>
  </div>
</template>
<script>
import axios from "axios";
export default {
  name: "edit-product",
  props: {
    productId: {
      type: String, // Adjust the type based on your needs (String, Number, etc.)
      required: true,
    },
  },
  data() {
    return {
      product: null,
      categories: null,
      selectedCategory: "",
      selectedProductType: "",
      selectedProductUnit: "",
      product_price: "",
      product_manufactured_date: "",
      product_expiry_date: "",
      image: null,
      error: "",
      message: "",
    };
  },
  created() {
    this.product = this.$store.state.productMaster[this.productId];
    this.categories = this.$store.state.categoryMaster;
    this.selectedCategory = this.product.category_id;
    this.selectedProductType = this.product.veg_nveg;
    this.selectedProductUnit = this.product.product_unit;
    this.product_manufactured_date = this.displayDate(
      this.product.product_man_date
    );
    this.product_expiry_date = this.displayDate(this.product.product_exp_date);
    this.product_price = this.displayNumber(
      this.product.product_price_per_unit
    );
  },
  methods: {
    displayDate(dateStr) {
      // When you need to display the date, convert it to YYYY-MM-DD format
      const date = new Date(dateStr);
      return date.toISOString().split("T")[0];
    },
    displayNumber(numStr) {
      return Number(Number(numStr).toFixed(2));
    },
    handleImageUpload(event) {
      this.image = event.target.files[0];
      console.log(event.target.files[0]);
    },
    async editProduct() {
      const formData = new FormData();
      formData.append("username", this.$store.state.user.username);
      formData.append("productId", this.productId);
      formData.append("product-name", this.product.name);
      formData.append("product-description", this.product.product_desc);
      formData.append("product-price", this.product_price);
      formData.append("product-quantity", this.product.product_stock);
      formData.append("product-type", this.selectedProductType);
      formData.append("product-unit", this.selectedProductUnit);
      formData.append("product-discount", this.product.product_discount);
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
        const response = await axios.put(
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
          alert("Product saved successfully");
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
  },
};
</script>

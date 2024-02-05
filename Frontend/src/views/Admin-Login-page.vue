<template>
  <div class="col-md-6 offset-md-3">
    <h2>Admin Login</h2>

    <!-- Login Form -->
    <form @submit.prevent="handleSubmit">
      <!-- Email Field -->
      <div class="form-group">
        <label for="email">Email:</label>
        <input
          type="email"
          class="form-control"
          v-model="email"
          id="email"
          placeholder="Enter your email"
          required
        />
      </div>

      <!-- Password Field -->
      <div class="form-group">
        <label for="password">Password:</label>
        <input
          type="password"
          class="form-control"
          v-model="password"
          id="password"
          placeholder="Enter your password"
          required
        />
      </div>

      <!-- Submit Button -->
      <button type="submit" class="btn btn-primary">Admin Login</button>
    </form>

    <div class="alert alert-danger mt-3" v-if="errorMsg">{{ errorMsg }}</div>
  </div>
</template>

<script>
// import axios from "axios";
import apiRequest from "@/api";

export default {
  name: "Admin-Login-page",
  data() {
    return {
      email: "",
      password: "",
      errorMsg: "",
    };
  },
  methods: {
    async handleSubmit() {
      this.errorMsg = ""; // resetting error msg
      console.log(this.email, this.password);

      const userData = {
        username: this.email,
        password: this.password,
      };
      // Set the content type to JSON
      // const config = {
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      // };
      try {
        const responseData = await apiRequest(
          "api/admin/login",
          "POST",
          userData,
          false
        );
        console.log("Admin Login successful:", responseData);
        //this.$store.commit("user", response.data);
        this.$store.commit("user", responseData);
        this.$store.commit("setUserType", "SM");
        this.$router.push("/admin");
      } catch (error) {
        console.log(error);
        if (error.response) {
          // The request was made, but the server responded with an HTTP error status code
          console.error(
            "HTTP error:",
            error.response.status,
            error.response.statusText
          );
          if (error.response.status == 401) {
            this.errorMsg = "Invalid Credentials !";
          }
        } else {
          // Something happened in setting up the request or during the request
          console.error("Request failed:", error.message);
          this.errorMsg = error.message;
        }
      }
    },
  },
};
</script>

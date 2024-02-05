<template>
  <div class="container">
    <h2>Registration Form</h2>
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          class="form-control"
          id="email"
          v-model="formData.username"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          class="form-control"
          id="password"
          v-model="formData.password"
          required
        />
      </div>
      <div class="form-group">
        <label for="confirmpassword">Confirm Password</label>
        <input
          type="password"
          class="form-control"
          id="confirmpassword"
          v-model="formData.confirmPassword"
          required
        />
      </div>
      <div class="form-group">
        <label for="firstName">First Name</label>
        <input
          type="text"
          class="form-control"
          id="firstName"
          v-model="formData.firstName"
          required
        />
      </div>
      <div class="form-group">
        <label for="lastName">Last Name</label>
        <input
          type="text"
          class="form-control"
          id="lastName"
          v-model="formData.lastName"
          required
        />
      </div>
      <div class="form-group">
        <label for="phoneNumber">Phone Number</label>
        <input
          type="tel"
          class="form-control"
          id="phoneNumber"
          v-model="formData.phoneNumber"
          required
        />
      </div>
      <div class="form-group">
        <label for="address">Address</label>
        <textarea
          class="form-control"
          id="address"
          rows="3"
          v-model="formData.address"
          required
        ></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Register</button>
    </form>
    <div class="alert alert-danger mt-3" v-if="errorMsg">{{ errorMsg }}</div>
  </div>
</template>

<script>
import apiRequest from "@/api";
export default {
  data() {
    return {
      errorMsg: "",
      formData: {
        username: "",
        password: "",
        confirmPassword: "",
        firstName: "",
        lastName: "",
        phoneNumber: "",
        address: "",
      },
    };
  },
  methods: {
    async submitForm() {
      // Handle form submission here
      // You can access the form data in this.formData
      console.log(this.formData);
      if (this.formData.password != this.formData.confirmPassword) {
        this.errorMsg =
          "password and confirm password fields are not matching!";
      } else {
        const userData = {
          username: this.formData.username,
          password: this.formData.password,
          firstName: this.formData.firstName,
          lastName: this.formData.lastName,
          phoneNumber: this.formData.phoneNumber,
          address: this.formData.address,
        };
        try {
          // Make a POST request to the /api/login endpoint using await
          //const response = await axios.post("api/login", userData, config);

          // Handle a successful JSON response
          //const responseData = response.data;

          const responseData = await apiRequest(
            "api/register",
            "POST",
            userData,
            false
          );
          console.log("Registration response:", responseData);
          if (responseData.code == "S") {
            this.errorMsg = "";
            alert("Registration Successful !");
            this.$router.push("/login");
          } else {
            this.errorMsg = responseData.msg;
          }
        } catch (error) {
          console.log(error);
          if (error.response) {
            // The request was made, but the server responded with an HTTP error status code
            console.error(
              "HTTP error:",
              error.response.status,
              error.response.statusText
            );
            if (error.response.data.error_message) {
              //error msg sent by api
              this.errorMsg = error.response.data.error_message;
            } else if (error.message) {
              //axios error msg
              this.errorMsg = error.message;
            } else {
              this.errorMsg = "some error occurred";
            }
          } else {
            // Something happened in setting up the request or during the request
            console.error("Request failed:", error.message);
            this.errorMsg = "some error occurred";
          }
        }
      }
    },
  },
};
</script>

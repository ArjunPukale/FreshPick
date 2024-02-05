<template>
  <div>
    <nav class="admin navbar navbar-expand-lg navbar-light fixed-top">
      <div class="container-fluid">
        <!-- Brand Name (Freshpick) on the left -->

        <router-link to="/admin" class="navbar-brand"
          >Freshpick-Admin</router-link
        >
        <!-- Add a button for small screens -->
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Navigation Links on the left (hidden on small screens) -->
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li v-if="isUserLoggedIn" class="nav-item">
              <router-link to="/admin/categoryManagement" class="nav-link"
                >Category Management</router-link
              >
            </li>
            <li v-if="isUserLoggedIn" class="nav-item">
              <!-- <a class="nav-link" href="#">Basket</a> -->
              <router-link to="/admin/productManagement" class="nav-link"
                >Product Management</router-link
              >
            </li>
          </ul>
        </div>

        <!-- Logout link on the right -->
        <ul class="navbar-nav ml-auto">
          <li v-if="isUserLoggedIn" class="nav-item">
            <a @click="logout" class="nav-link">Logout</a>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>
<style scoped>
.nav-link {
  cursor: pointer;
}
</style>
<script>
import apiRequest from "@/api";
export default {
  name: "Nav-bar",
  computed: {
    isUserLoggedIn() {
      return this.$store.state.user != null;
    },
    reports() {
      return this.$store.state.adminReports;
    },
  },
  created() {
    this.startTimer();
  },
  methods: {
    startTimer() {
      this.intervalId = setInterval(() => {
        console.log("Notification timer hit");
        for (const reportId in this.reports) {
          if (this.reports[reportId] == "N") {
            this.getReportStatus(reportId);
          }
        }
      }, 5000); // Updates the timer every 5 seconds (5000ms)
    },
    async getReportStatus(reportId) {
      const userData = { username: this.$store.state.user.username };
      try {
        const responseData = await apiRequest(
          "api/admin/productReport?username=" +
            encodeURIComponent(this.$store.state.user.username) +
            "&reportId=" +
            encodeURIComponent(reportId),
          "GET",
          userData,
          true
        );
        if (responseData.code == "S") {
          let status = responseData.status;
          this.$store.commit("updateReportStatus", {
            reportId: reportId,
            status: status,
          });
          if (status == "Y") {
            alert("Report ready!!! download started ...");
            const csvData = atob(responseData.csv_data);
            // Create a Blob from the CSV data
            const blob = new Blob([csvData], { type: "text/csv" });
            // Create a download link for the file
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
              "download",
              responseData.filename || "product_report.csv"
            );
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          }
        }
      } catch (error) {
        console.log(error);
      }
    },
    methods: {
      logout() {
        this.$store.commit("user", null);
      },
    },
  },
};
</script>

<template>
  <div class="container-fluid" style="margin-top: 55px">
    <h2 style="margin-bottom: 25px">Reports</h2>
    <div class="row" style="display: inline-flex">
      <div class="col">
        <button @click="generateProdRep" type="button" class="btn btn-primary">
          Product Report
        </button>
      </div>
      <!-- <div class="col">
        <button type="button" class="btn btn-secondary">Button 2</button>
      </div>
      <div class="col">
        <button type="button" class="btn btn-success">Button 3</button>
      </div> -->
    </div>
  </div>
</template>
<script>
import apiRequest from "@/api";
export default {
  name: "adminReports",
  data() {
    return {
      reportId: null,
    };
  },
  computed: {},
  methods: {
    async generateProdRep() {
      const userData = {
        username: this.$store.state.user.username,
      };
      try {
        const responseData = await apiRequest(
          "api/admin/productReport",
          "POST",
          userData,
          true
        );
        if (responseData.code == "S") {
          this.reportId = responseData.report_id;
          this.$store.commit("AddReport", this.reportId);
          alert("your report will be downloaded shortly !");
        } else {
          alert("Something went wrong !");
        }
      } catch (error) {
        console.log(error);
        alert("Error");
      }
    },
  },
};
</script>

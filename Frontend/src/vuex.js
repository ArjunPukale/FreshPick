import Vuex from "vuex";

const state = {
  user: null,
  categoryMaster: {},
  productMaster: {},
  imageEndpoint: "http://127.0.0.1:8080/static/images/",
  apiBaseUrl: "http://127.0.0.1:8080/",
  userType: "N", //N=Normal, SM=StoreManager,
  adminReports: {},
};

const store = new Vuex.Store({
  state,
  getters: {
    user: (state) => {
      return state.user;
    },
  },

  mutations: {
    user(state, user) {
      state.user = user;
    },
    setCategoryMaster(state, data) {
      state.categoryMaster = data;
    },
    setProductMaster(state, data) {
      state.productMaster = data;
    },
    setUserBasket(state, basket) {
      if (state.user) {
        state.user.basket = basket;
      }
    },
    setUserType(state, user_type) {
      state.userType = user_type;
    },
    AddReport(state, reportId) {
      // Assuming payload is an object with key-value to add
      state.adminReports[reportId] = "N";
    },
    updateReportStatus(state, payload) {
      const { reportId, status } = payload;
      state.adminReports[reportId] = status;
    },
  },
  actions: {},
});

export default store;

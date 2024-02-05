import axios from "axios";
import router from "./router";
import store from "./vuex";

async function apiRequest(endpoint, method, data, handle_401) {
  let token = "";
  if (store.state.user) {
    token = store.state.user.token;
  }
  // const headers_get = {
  //   Authorization: `Bearer ${token}`,
  // };
  const headers = {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
  try {
    const response = await axios({
      method: method,
      url: endpoint,
      //data: method !== "GET" ? data : undefined,
      data: ["GET","DELETE"].includes(method) ? undefined : data,
      headers: headers,
    });

    return response.data;
  } catch (error) {
    if (handle_401 && error.response && error.response.status == 401) {
      alert("Session Expired");
      store.commit("user", null);
      router.push("/login");
    } else {
      throw error;
    }
  }
}

export default apiRequest;

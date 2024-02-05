import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home-page.vue";
import Login from "../views/Login-page.vue";
import Register from "../views/Registration-page.vue";
import Basket from "../views/BasketView.vue";
import OrderConfirmation from "../views/Order-Confirmation-page.vue";
import myOrders from "../views/MyOrders.vue";
import advancedSearch from "../views/Advanced-search.vue";

import AdminLogin from "../views/Admin-Login-page.vue";
import AdminHome from "../views/Admin-Home-page.vue";
import CategoryManagement from "../views/Category-Management.vue";
import ProductManagement from "../views/Product-Management.vue";
import AddCategory from "../views/Admin-add-category.vue";
import AddProduct from "../views/Admin-add-product.vue";
import EditCategoryComponent from "../views/Admin-edit-category.vue";
import EditProductComponent from "../views/Admin-edit-product.vue";

import store from "@/vuex";
const routes = [
  {
    path: "/",
    component: Home,
  },
  {
    path: "/login",
    component: Login,
  },
  {
    path: "/register",
    component: Register,
  },
  {
    path: "/basket",
    component: Basket,
    meta: { requiresAuth: true }, // Add a custom 'requiresAuth' property
  },
  {
    path: "/orderConfirmation",
    component: OrderConfirmation,
    meta: { requiresAuth: true },
  },
  {
    path: "/orders",
    component: myOrders,
    meta: { requiresAuth: true },
  },
  {
    path: "/searchProduct/:queryStr",
    name: "searchProduct",
    props: true,
    component: advancedSearch,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/login",
    component: AdminLogin,
  },
  {
    path: "/admin",
    component: AdminHome,
  },
  {
    path: "/admin/categoryManagement",
    component: CategoryManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/productManagement",
    component: ProductManagement,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/category/add",
    component: AddCategory,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/product/add",
    component: AddProduct,
    meta: { requiresAuth: true },
  },
  {
    path: "/admin/category/edit/:categoryId",
    name: "editCategory",
    component: EditCategoryComponent,
    props: true,
  },
  {
    path: "/admin/product/edit/:productId",
    name: "editProduct",
    component: EditProductComponent,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

// Define a navigation guard
router.beforeEach((to, from, next) => {
  const user = store.state.user; // Assuming 'user' is stored in your Vuex store
  const requiresAuth = to.meta.requiresAuth;

  if (requiresAuth && user === null) {
    // If the route requires authentication and the user is not logged in, redirect to the login page
    next("/login");
  } else {
    // Allow access to the route
    next();
  }
});
export default router;

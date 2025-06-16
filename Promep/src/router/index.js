import { createRouter, createWebHashHistory } from "vue-router";
import Home from "../views/Home.vue";
import CreateRequest from "../views/CreateRequest.vue";

const routes = [
  {
	path: "/",
	name: "Home",
	component: Home,
  },
  {
	path: "/create-request",
	name: "CreateRequest",
	component: CreateRequest,
  },
  {
	path: "/requests",
	name: "RequestsList",
	component: () => import("../views/RequestsList.vue"),
  },
  {
	path: "/request/:id",
	name: "RequestDetail",
	component: () => import("../views/RequestDetail.vue"),
	props: true
  },
  // Catch-all route for unmatched paths
  {
	path: "/:pathMatch(.*)*",
	redirect: "/"
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;

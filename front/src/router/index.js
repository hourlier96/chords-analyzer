import { createRouter, createWebHistory } from "vue-router";

const ProgressionAnalyzerView = () =>
  import("@/views/ProgressionAnalyzerView.vue");

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "progression_analyzer",
      component: ProgressionAnalyzerView,
    },
  ],
});

export default router;

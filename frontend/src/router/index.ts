import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/campaigns" },
    {
      path: "/campaigns",
      name: "campaigns",
      component: () => import("@/pages/CampaignList.vue"),
    },
    {
      path: "/campaigns/new",
      name: "campaign-new",
      component: () => import("@/pages/CampaignWizard.vue"),
    },
    {
      path: "/campaigns/:id/keywords",
      name: "keywords",
      component: () => import("@/pages/KeywordReview.vue"),
    },
    {
      path: "/campaigns/:id",
      name: "lead-board",
      component: () => import("@/pages/LeadBoard.vue"),
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
});

export default router;

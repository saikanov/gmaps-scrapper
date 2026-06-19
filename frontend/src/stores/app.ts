import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api/client";
import type { Health } from "@/api/types";

export const useAppStore = defineStore("app", () => {
  const health = ref<Health | null>(null);

  async function loadHealth() {
    try {
      health.value = await api.health();
    } catch {
      health.value = null;
    }
  }

  return { health, loadHealth };
});

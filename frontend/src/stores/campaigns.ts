import { defineStore } from "pinia";
import { ref } from "vue";
import { api } from "@/api/client";
import type { Campaign } from "@/api/types";

export const useCampaignStore = defineStore("campaigns", () => {
  const list = ref<Campaign[]>([]);
  const current = ref<Campaign | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadList() {
    loading.value = true;
    error.value = null;
    try {
      list.value = await api.listCampaigns();
    } catch (e: any) {
      error.value = e?.message ?? "Failed to load campaigns";
    } finally {
      loading.value = false;
    }
  }

  async function loadOne(id: string) {
    current.value = await api.getCampaign(id);
    return current.value;
  }

  return { list, current, loading, error, loadList, loadOne };
});

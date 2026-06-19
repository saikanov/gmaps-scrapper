<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import { useToast } from "primevue/usetoast";
import PageHeader from "@/components/PageHeader.vue";
import { api } from "@/api/client";

const router = useRouter();
const toast = useToast();

const BUYER_TYPES = [
  { key: "importer", label: "Importer", hint: "brings the commodity into the country" },
  { key: "distributor", label: "Distributor", hint: "moves volume to resellers" },
  { key: "wholesaler", label: "Wholesaler", hint: "bulk supply to trade" },
  { key: "manufacturer", label: "Manufacturer", hint: "consumes the commodity" },
  { key: "retailer", label: "Retailer / HORECA", hint: "end-consumer facing" },
];

const form = reactive({
  commodity: "",
  country: "",
  buyer_profile: ["importer", "distributor"] as string[],
  keyword_mode: "tiering" as "tiering" | "all_at_once",
});

const submitting = ref(false);

const valid = computed(
  () => form.commodity.trim() && form.country.trim() && form.buyer_profile.length > 0,
);

function toggle(key: string) {
  const i = form.buyer_profile.indexOf(key);
  if (i >= 0) form.buyer_profile.splice(i, 1);
  else form.buyer_profile.push(key);
}

async function submit() {
  if (!valid.value || submitting.value) return;
  submitting.value = true;
  try {
    const campaign = await api.createCampaign({
      commodity: form.commodity.trim(),
      country: form.country.trim(),
      buyer_profile: form.buyer_profile,
      keyword_mode: form.keyword_mode,
    });
    toast.add({ severity: "success", summary: "Campaign created", life: 2500 });
    router.push(`/campaigns/${campaign.id}/keywords?gen=1`);
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: "Could not create campaign",
      detail: e?.response?.data?.detail ?? e?.message,
      life: 4000,
    });
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <PageHeader eyebrow="Step 1 of 2" title="New campaign" subtitle="Define the target. AI writes the keywords next." />

  <section class="flex-1 overflow-auto px-8 py-8">
    <div class="mx-auto max-w-2xl">
      <div class="space-y-7 rounded-card border border-ink/8 bg-white p-8 shadow-card">
        <!-- commodity -->
        <div>
          <label class="eyebrow mb-2 block">Commodity</label>
          <input
            v-model="form.commodity"
            type="text"
            placeholder="green coffee beans"
            class="w-full rounded-lg border border-ink/15 bg-white px-3.5 py-2.5 text-[15px] outline-none transition-colors focus:border-gold"
          />
        </div>

        <!-- country -->
        <div>
          <label class="eyebrow mb-2 block">Target market</label>
          <input
            v-model="form.country"
            type="text"
            placeholder="Germany"
            class="w-full rounded-lg border border-ink/15 bg-white px-3.5 py-2.5 text-[15px] outline-none transition-colors focus:border-gold"
          />
          <p class="mt-1.5 text-[12px] text-ink-300">
            Keywords are written in this country's business language.
          </p>
        </div>

        <!-- buyer profile -->
        <div>
          <label class="eyebrow mb-2 block">Buyer profile</label>
          <div class="grid gap-2 sm:grid-cols-2">
            <button
              v-for="b in BUYER_TYPES"
              :key="b.key"
              type="button"
              class="flex items-start gap-3 rounded-lg border px-3.5 py-3 text-left transition-colors"
              :class="
                form.buyer_profile.includes(b.key)
                  ? 'border-gold bg-gold-50'
                  : 'border-ink/12 bg-white hover:border-ink/25'
              "
              @click="toggle(b.key)"
            >
              <span
                class="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border"
                :class="
                  form.buyer_profile.includes(b.key)
                    ? 'border-gold bg-gold text-ink'
                    : 'border-ink/30'
                "
              >
                <i v-if="form.buyer_profile.includes(b.key)" class="pi pi-check text-[9px]" />
              </span>
              <span>
                <span class="block text-[14px] font-medium text-ink">{{ b.label }}</span>
                <span class="block text-[12px] text-ink-300">{{ b.hint }}</span>
              </span>
            </button>
          </div>
        </div>

        <!-- keyword mode -->
        <div>
          <label class="eyebrow mb-2 block">Keyword mode</label>
          <div class="grid gap-2 sm:grid-cols-2">
            <button
              type="button"
              class="rounded-lg border px-4 py-3 text-left transition-colors"
              :class="form.keyword_mode === 'tiering' ? 'border-gold bg-gold-50' : 'border-ink/12 hover:border-ink/25'"
              @click="form.keyword_mode = 'tiering'"
            >
              <span class="block text-[14px] font-semibold text-ink">Tiering · saves budget</span>
              <span class="block text-[12px] text-ink-300">Dispatch trade-hub (tier 1) ports first.</span>
            </button>
            <button
              type="button"
              class="rounded-lg border px-4 py-3 text-left transition-colors"
              :class="form.keyword_mode === 'all_at_once' ? 'border-gold bg-gold-50' : 'border-ink/12 hover:border-ink/25'"
              @click="form.keyword_mode = 'all_at_once'"
            >
              <span class="block text-[14px] font-semibold text-ink">All at once</span>
              <span class="block text-[12px] text-ink-300">Full matrix. More volume, more load.</span>
            </button>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 border-t border-ink/8 pt-5">
          <Button text label="Cancel" severity="secondary" @click="router.push('/campaigns')" />
          <Button
            label="Generate keywords"
            icon="pi pi-sparkles"
            :loading="submitting"
            :disabled="!valid"
            @click="submit"
          />
        </div>
      </div>
    </div>
  </section>
</template>

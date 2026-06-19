<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import Button from "primevue/button";
import Skeleton from "primevue/skeleton";
import { useToast } from "primevue/usetoast";
import PageHeader from "@/components/PageHeader.vue";
import { api } from "@/api/client";
import type { KeywordPlan, KeywordQuery } from "@/api/types";

const route = useRoute();
const router = useRouter();
const toast = useToast();
const id = route.params.id as string;

const plan = ref<KeywordPlan | null>(null);
const loading = ref(true);
const generating = ref(false);
const dispatching = ref(false);
const error = ref<string | null>(null);

// selection keyed by query string
const selected = reactive<Record<string, boolean>>({});
const tier2Open = ref(false);
const manual = ref("");

const tier1 = computed(() => plan.value?.queries.filter((q) => q.tier === 1) ?? []);
const tier2 = computed(() => plan.value?.queries.filter((q) => q.tier >= 2) ?? []);
const selectedCount = computed(
  () => Object.values(selected).filter(Boolean).length,
);

function applyPlan(p: KeywordPlan) {
  plan.value = p;
  for (const q of p.queries) selected[q.query] = q.tier === 1; // tier-1 pre-checked
}

async function load() {
  loading.value = true;
  error.value = null;
  try {
    if (route.query.gen === "1") {
      generating.value = true;
      applyPlan(await api.generateKeywords(id));
    } else {
      try {
        applyPlan(await api.getKeywords(id));
      } catch {
        applyPlan(await api.generateKeywords(id));
      }
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? e?.message ?? "Failed to load keywords";
  } finally {
    loading.value = false;
    generating.value = false;
  }
}

async function regenerate() {
  generating.value = true;
  try {
    applyPlan(await api.generateKeywords(id));
    toast.add({ severity: "success", summary: "Keywords regenerated", life: 2000 });
  } catch (e: any) {
    toast.add({ severity: "error", summary: "Regenerate failed", detail: e?.message, life: 3500 });
  } finally {
    generating.value = false;
  }
}

function addManual() {
  const q = manual.value.trim();
  if (!q || !plan.value) return;
  if (!plan.value.queries.find((x) => x.query === q)) {
    plan.value.queries.push({ query: q, city: "", tier: 1 });
    selected[q] = true;
  }
  manual.value = "";
}

async function dispatch() {
  if (!plan.value || selectedCount.value === 0) return;
  dispatching.value = true;
  const queries: KeywordQuery[] = plan.value.queries
    .filter((q) => selected[q.query])
    .map((q) => ({ query: q.query, city: q.city, tier: q.tier }));
  try {
    const res = await api.dispatch(id, queries);
    toast.add({
      severity: "success",
      summary: "Dispatched to scraper",
      detail: res.detail,
      life: 3000,
    });
    router.push(`/campaigns/${id}`);
  } catch (e: any) {
    toast.add({ severity: "error", summary: "Dispatch failed", detail: e?.message, life: 4000 });
  } finally {
    dispatching.value = false;
  }
}

onMounted(load);
</script>

<template>
  <PageHeader
    eyebrow="Step 2 of 2 · Approve before dispatch"
    title="Keyword review"
    :subtitle="plan ? `Language: ${plan.language.toUpperCase()} · cities ranked by trade hub` : 'Generating…'"
  >
    <template #actions>
      <Button
        text
        severity="secondary"
        label="Regenerate"
        icon="pi pi-refresh"
        :loading="generating"
        @click="regenerate"
      />
      <Button
        :label="`Dispatch ${selectedCount} →`"
        icon="pi pi-send"
        :loading="dispatching"
        :disabled="selectedCount === 0"
        @click="dispatch"
      />
    </template>
  </PageHeader>

  <section class="flex-1 overflow-auto px-8 py-6">
    <div class="mx-auto max-w-3xl space-y-5">
      <!-- loading -->
      <template v-if="loading">
        <div class="rounded-card border border-ink/8 bg-white p-6 shadow-card">
          <Skeleton width="30%" height="0.9rem" class="mb-4" />
          <Skeleton v-for="n in 6" :key="n" width="100%" height="2.2rem" class="mb-2" />
        </div>
        <p class="text-center text-[13px] text-ink-300">
          <i class="pi pi-spin pi-spinner mr-1" /> AI is localizing keywords and ranking trade hubs…
        </p>
      </template>

      <!-- error -->
      <div
        v-else-if="error"
        class="rounded-card border border-red-200 bg-red-50 px-5 py-4 text-sm text-status-rejected"
      >
        {{ error }}
        <button class="ml-2 font-semibold underline" @click="load">Retry</button>
      </div>

      <template v-else-if="plan">
        <!-- term context -->
        <div class="flex flex-wrap gap-x-6 gap-y-2 rounded-card border border-ink/8 bg-white px-5 py-4 text-[12px] shadow-card">
          <div>
            <div class="eyebrow mb-1">Buyer terms</div>
            <span class="text-ink-700">{{ plan.buyer_terms.join(" · ") }}</span>
          </div>
          <div>
            <div class="eyebrow mb-1">Commodity terms</div>
            <span class="text-ink-700">{{ plan.commodity_terms.join(" · ") }}</span>
          </div>
        </div>

        <!-- Tier 1 -->
        <div class="rounded-card border border-ink/8 bg-white shadow-card">
          <div class="flex items-center gap-2 border-b border-ink/8 px-5 py-3">
            <span class="rounded bg-amber-50 px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-amber ring-1 ring-inset ring-amber/30">
              Tier 1 · ports & hubs
            </span>
            <span class="text-[12px] text-ink-300">{{ tier1.length }} queries — dispatched first</span>
          </div>
          <ul class="divide-y divide-ink/6">
            <li
              v-for="q in tier1"
              :key="q.query"
              class="flex items-center gap-3 px-5 py-2.5 hover:bg-paper/60"
            >
              <input type="checkbox" v-model="selected[q.query]" class="h-4 w-4 accent-gold" />
              <span class="flex-1 text-[14px] text-ink">{{ q.query }}</span>
              <span v-if="q.city" class="text-[12px] text-ink-300">{{ q.city }}</span>
            </li>
          </ul>
        </div>

        <!-- Tier 2 accordion -->
        <div v-if="tier2.length" class="rounded-card border border-ink/8 bg-white shadow-card">
          <button
            class="flex w-full items-center justify-between px-5 py-3"
            @click="tier2Open = !tier2Open"
          >
            <span class="flex items-center gap-2">
              <span class="rounded bg-paper px-2 py-0.5 text-[11px] font-bold uppercase tracking-wide text-ink-500 ring-1 ring-inset ring-ink/10">
                Tier 2 · inland markets
              </span>
              <span class="text-[12px] text-ink-300">{{ tier2.length }} queries</span>
            </span>
            <i :class="['pi', tier2Open ? 'pi-chevron-up' : 'pi-chevron-down', 'text-ink-300']" />
          </button>
          <ul v-show="tier2Open" class="divide-y divide-ink/6 border-t border-ink/8">
            <li
              v-for="q in tier2"
              :key="q.query"
              class="flex items-center gap-3 px-5 py-2.5 hover:bg-paper/60"
            >
              <input type="checkbox" v-model="selected[q.query]" class="h-4 w-4 accent-gold" />
              <span class="flex-1 text-[14px] text-ink">{{ q.query }}</span>
              <span v-if="q.city" class="text-[12px] text-ink-300">{{ q.city }}</span>
            </li>
          </ul>
        </div>

        <!-- manual add -->
        <div class="flex gap-2">
          <input
            v-model="manual"
            type="text"
            placeholder="+ Add a keyword manually"
            class="flex-1 rounded-lg border border-ink/15 bg-white px-3.5 py-2 text-[14px] outline-none focus:border-gold"
            @keyup.enter="addManual"
          />
          <Button text label="Add" icon="pi pi-plus" severity="secondary" @click="addManual" />
        </div>

        <!-- dispatch estimate -->
        <div class="sticky bottom-0 flex items-center justify-between rounded-card border border-gold/20 bg-gold-50 px-5 py-3">
          <span class="text-[13px] text-ink-700">
            <strong class="tnum">{{ selectedCount }}</strong> queries selected · 1 query = 1 scrape job
          </span>
          <Button
            :label="`Dispatch ${selectedCount} →`"
            icon="pi pi-send"
            :loading="dispatching"
            :disabled="selectedCount === 0"
            @click="dispatch"
          />
        </div>
      </template>
    </div>
  </section>
</template>

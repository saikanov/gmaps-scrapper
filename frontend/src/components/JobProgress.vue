<script setup lang="ts">
import { computed } from "vue";
import type { Job } from "@/api/types";

const props = defineProps<{ jobs: Job[] }>();

const active = new Set(["pending", "dispatched", "running"]);
const done = new Set(["ingested", "completed"]);

const stats = computed(() => {
  const total = props.jobs.length;
  const finished = props.jobs.filter((j) => done.has(j.status)).length;
  const running = props.jobs.filter((j) => active.has(j.status)).length;
  const failed = props.jobs.filter((j) => j.status === "error").length;
  const leads = props.jobs.reduce((s, j) => s + (j.leads_found || 0), 0);
  return { total, finished, running, failed, leads, pct: total ? Math.round((finished / total) * 100) : 0 };
});

const byTier = computed(() => {
  const map = new Map<number, { total: number; done: number }>();
  for (const j of props.jobs) {
    const t = map.get(j.tier) ?? { total: 0, done: 0 };
    t.total++;
    if (done.has(j.status)) t.done++;
    map.set(j.tier, t);
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]);
});
</script>

<template>
  <div v-if="stats.running > 0" class="rounded-card border border-gold/20 bg-gold-50 px-5 py-3.5">
    <div class="flex items-center justify-between">
      <span class="flex items-center gap-2 text-[13px] font-medium text-ink-700">
        <i class="pi pi-spin pi-spinner text-gold-deep" />
        Scraping in progress · {{ stats.finished }}/{{ stats.total }} jobs · {{ stats.leads }} leads ingested
      </span>
      <span class="tnum text-[13px] font-semibold text-gold-deep">{{ stats.pct }}%</span>
    </div>
    <div class="mt-2.5 flex gap-3">
      <div v-for="[tier, t] in byTier" :key="tier" class="flex-1">
        <div class="mb-1 flex items-center justify-between text-[11px] text-ink-500">
          <span>Tier {{ tier }}</span>
          <span class="tnum">{{ t.done }}/{{ t.total }}</span>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-white">
          <div
            class="h-full rounded-full bg-gold transition-all"
            :style="{ width: (t.total ? (t.done / t.total) * 100 : 0) + '%' }"
          />
        </div>
      </div>
    </div>
  </div>

  <div
    v-else-if="stats.failed > 0"
    class="rounded-card border border-amber/30 bg-amber-50 px-5 py-3 text-[13px] text-ink-700"
  >
    <i class="pi pi-exclamation-triangle mr-1.5 text-amber" />
    {{ stats.finished }}/{{ stats.total }} jobs done · {{ stats.failed }} failed.
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Skeleton from "primevue/skeleton";
import PageHeader from "@/components/PageHeader.vue";
import { useCampaignStore } from "@/stores/campaigns";
import type { Campaign } from "@/api/types";

const router = useRouter();
const store = useCampaignStore();

onMounted(() => store.loadList());

const empty = computed(() => !store.loading && store.list.length === 0);

function open(c: Campaign) {
  // No leads yet and no scrape running -> send to keyword review, else board.
  if (c.lead_count === 0 && c.jobs_running === 0 && c.jobs_done === 0) {
    router.push(`/campaigns/${c.id}/keywords`);
  } else {
    router.push(`/campaigns/${c.id}`);
  }
}

function buyerChips(c: Campaign): string[] {
  return c.buyer_profile ? c.buyer_profile.split(",").filter(Boolean) : [];
}

function progress(c: Campaign): number {
  if (c.job_count === 0) return 0;
  return Math.round((c.jobs_done / c.job_count) * 100);
}
</script>

<template>
  <PageHeader
    eyebrow="Workspace"
    title="Campaigns"
    subtitle="One campaign = one commodity × one market."
  >
    <template #actions>
      <Button
        label="New campaign"
        icon="pi pi-plus"
        @click="router.push('/campaigns/new')"
      />
    </template>
  </PageHeader>

  <section class="flex-1 overflow-auto px-8 py-6">
    <!-- loading -->
    <div v-if="store.loading" class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 6" :key="n" class="rounded-card border border-ink/8 bg-white p-5 shadow-card">
        <Skeleton width="60%" height="1.1rem" class="mb-3" />
        <Skeleton width="40%" height="0.8rem" class="mb-4" />
        <Skeleton width="100%" height="0.5rem" />
      </div>
    </div>

    <!-- error -->
    <div
      v-else-if="store.error"
      class="rounded-card border border-red-200 bg-red-50 px-5 py-4 text-sm text-status-rejected"
    >
      {{ store.error }}
      <button class="ml-2 font-semibold underline" @click="store.loadList()">Retry</button>
    </div>

    <!-- empty -->
    <div
      v-else-if="empty"
      class="mx-auto mt-16 max-w-md rounded-card border border-dashed border-ink/15 bg-white px-8 py-12 text-center"
    >
      <div
        class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gold-50 text-gold-deep"
      >
        <i class="pi pi-compass text-xl" />
      </div>
      <h3 class="font-display text-lg font-semibold text-ink">No campaigns yet</h3>
      <p class="mt-1 text-sm text-ink-500">
        Start one to generate keywords and find buyers on the map.
      </p>
      <Button
        class="mt-5"
        label="New campaign"
        icon="pi pi-plus"
        @click="router.push('/campaigns/new')"
      />
    </div>

    <!-- list -->
    <div v-else class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <button
        v-for="c in store.list"
        :key="c.id"
        class="group rounded-card border border-ink/8 bg-white p-5 text-left shadow-card transition-all hover:-translate-y-0.5 hover:border-gold/30 hover:shadow-md"
        @click="open(c)"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="font-display text-[16px] font-semibold leading-snug text-ink">
              {{ c.commodity }}
            </h3>
            <div class="mt-0.5 flex items-center gap-1.5 text-[13px] text-ink-500">
              <i class="pi pi-map-marker text-[11px]" />{{ c.country }}
            </div>
          </div>
          <span class="tnum text-[15px] font-semibold text-gold-deep">{{ c.lead_count }}</span>
        </div>

        <div class="mt-3 flex flex-wrap gap-1">
          <span
            v-for="b in buyerChips(c)"
            :key="b"
            class="rounded bg-paper px-1.5 py-0.5 text-[11px] font-medium capitalize text-ink-500 ring-1 ring-inset ring-ink/8"
            >{{ b }}</span
          >
        </div>

        <!-- scrape progress -->
        <div class="mt-4">
          <div class="mb-1 flex items-center justify-between text-[11px] text-ink-300">
            <span v-if="c.jobs_running > 0" class="flex items-center gap-1 text-gold-deep">
              <i class="pi pi-spin pi-spinner text-[10px]" />
              scraping · {{ c.jobs_done }}/{{ c.job_count }}
            </span>
            <span v-else>{{ c.job_count > 0 ? `${c.jobs_done}/${c.job_count} jobs` : "not dispatched" }}</span>
            <span class="tnum">{{ progress(c) }}%</span>
          </div>
          <div class="h-1.5 overflow-hidden rounded-full bg-paper">
            <div
              class="h-full rounded-full bg-gold transition-all"
              :style="{ width: progress(c) + '%' }"
            />
          </div>
        </div>
      </button>
    </div>
  </section>
</template>

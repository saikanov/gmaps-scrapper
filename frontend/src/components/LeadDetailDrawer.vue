<script setup lang="ts">
import Drawer from "primevue/drawer";
import ScoreBadge from "./ScoreBadge.vue";
import BuyerTypeBadge from "./BuyerTypeBadge.vue";
import StatusBadge from "./StatusBadge.vue";
import type { Lead, OutreachStatus } from "@/api/types";

defineProps<{ lead: Lead | null }>();
const visible = defineModel<boolean>("visible", { default: false });
const emit = defineEmits<{ (e: "setStatus", s: OutreachStatus): void }>();

const STATUSES: OutreachStatus[] = [
  "new",
  "contacted",
  "replied",
  "qualified",
  "rejected",
  "won",
];
</script>

<template>
  <Drawer v-model:visible="visible" position="right" class="!w-[440px]">
    <template #header>
      <span class="font-display text-[15px] font-semibold text-ink">Lead detail</span>
    </template>
    <div v-if="lead" class="space-y-6">
      <div>
        <div class="flex items-start justify-between gap-3">
          <h2 class="font-display text-[18px] font-semibold leading-tight text-ink">{{ lead.name }}</h2>
          <ScoreBadge :score="lead.score" />
        </div>
        <div class="mt-1.5 flex items-center gap-2">
          <BuyerTypeBadge :type="lead.lead_type" />
          <span class="text-ink-300">·</span>
          <span class="text-[13px] text-ink-500">{{ lead.category || "—" }}</span>
        </div>
      </div>

      <!-- AI reasoning -->
      <div v-if="lead.score_reason" class="rounded-lg border border-ink/8 bg-paper px-4 py-3">
        <div class="eyebrow mb-1">Why this score</div>
        <p class="text-[13px] leading-relaxed text-ink-700">{{ lead.score_reason }}</p>
      </div>

      <!-- enrichment -->
      <div v-if="lead.enrichment" class="rounded-lg border border-gold/20 bg-gold-50 px-4 py-3">
        <div class="eyebrow mb-1 text-gold-deep">Enrichment</div>
        <p v-if="lead.enrichment.summary" class="text-[13px] leading-relaxed text-ink-700">
          {{ lead.enrichment.summary }}
        </p>
        <p v-if="lead.enrichment.best_email" class="mt-1 text-[13px]">
          <span class="text-ink-300">Real email:</span> {{ lead.enrichment.best_email }}
        </p>
      </div>

      <!-- contact -->
      <dl class="space-y-2.5 text-[13px]">
        <div class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Phone</dt>
          <dd class="tnum text-ink-700">{{ lead.phone || "—" }}</dd>
        </div>
        <div class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Email</dt>
          <dd class="text-ink-700">{{ lead.email || "—" }}</dd>
        </div>
        <div class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Website</dt>
          <dd class="truncate">
            <a v-if="lead.website" :href="lead.website" target="_blank" class="text-gold-deep hover:underline">
              {{ lead.website }}
            </a>
            <span v-else class="text-ink-700">—</span>
          </dd>
        </div>
        <div class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Address</dt>
          <dd class="text-ink-700">{{ lead.address || "—" }}</dd>
        </div>
        <div class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Reviews</dt>
          <dd class="tnum text-ink-700">
            {{ lead.review_count }} <span v-if="lead.review_rating">· {{ lead.review_rating }}★</span>
          </dd>
        </div>
        <div v-if="lead.gmaps_url" class="flex gap-3">
          <dt class="w-20 shrink-0 text-ink-300">Maps</dt>
          <dd>
            <a :href="lead.gmaps_url" target="_blank" class="text-gold-deep hover:underline">Open in Google Maps</a>
          </dd>
        </div>
      </dl>

      <!-- provenance -->
      <div v-if="lead.provenance?.length">
        <div class="eyebrow mb-1.5">Found by</div>
        <div class="flex flex-wrap gap-1">
          <span
            v-for="(p, i) in lead.provenance"
            :key="i"
            class="rounded bg-paper px-1.5 py-0.5 text-[11px] text-ink-500 ring-1 ring-inset ring-ink/8"
          >
            {{ p.query }}
          </span>
        </div>
      </div>

      <!-- outreach -->
      <div class="border-t border-ink/8 pt-4">
        <div class="mb-2 flex items-center justify-between">
          <span class="eyebrow">Outreach</span>
          <StatusBadge :status="lead.outreach_status" />
        </div>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="s in STATUSES"
            :key="s"
            class="rounded-md border px-2.5 py-1 text-[12px] font-medium capitalize transition-colors"
            :class="
              lead.outreach_status === s
                ? 'border-gold bg-gold text-ink'
                : 'border-ink/12 text-ink-500 hover:border-ink/30'
            "
            @click="emit('setStatus', s)"
          >
            {{ s }}
          </button>
        </div>
      </div>
    </div>
  </Drawer>
</template>

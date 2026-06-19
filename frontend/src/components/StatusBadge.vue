<script setup lang="ts">
import { computed } from "vue";
import type { OutreachStatus } from "@/api/types";

const props = defineProps<{ status: OutreachStatus }>();

// Customs-stamp style chips; colors locked by requirements §12.2.
const MAP: Record<OutreachStatus, { label: string; cls: string }> = {
  new: { label: "New", cls: "bg-slate-100 text-status-new ring-slate-200" },
  contacted: { label: "Contacted", cls: "bg-blue-50 text-status-contacted ring-blue-200" },
  replied: { label: "Replied", cls: "bg-indigo-50 text-status-replied ring-indigo-200" },
  qualified: { label: "Qualified", cls: "bg-green-50 text-status-qualified ring-green-200" },
  rejected: { label: "Rejected", cls: "bg-red-50 text-status-rejected ring-red-200" },
  won: { label: "Won", cls: "bg-amber-50 text-status-won ring-amber-200" },
};
const meta = computed(() => MAP[props.status] ?? MAP.new);
</script>

<template>
  <span
    class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ring-1 ring-inset"
    :class="meta.cls"
  >
    {{ meta.label }}
  </span>
</template>

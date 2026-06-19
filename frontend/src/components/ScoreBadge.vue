<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{ score: number | null }>();

// Score reads like a cargo-class marking: mono numerals, color by band.
const band = computed(() => {
  const s = props.score;
  if (s === null || s === undefined) return { cls: "text-ink-300 bg-paper ring-ink-300/20", val: "—" };
  if (s >= 80) return { cls: "text-gold-deep bg-gold-50 ring-gold/30", val: String(s) };
  if (s >= 60) return { cls: "text-amber bg-amber-50 ring-amber/30", val: String(s) };
  if (s >= 40) return { cls: "text-status-contacted bg-blue-50 ring-blue-200", val: String(s) };
  return { cls: "text-status-rejected bg-red-50 ring-red-200", val: String(s) };
});
</script>

<template>
  <span
    class="tnum inline-flex min-w-[2.5rem] items-center justify-center rounded-md px-1.5 py-0.5 text-[13px] font-semibold ring-1 ring-inset"
    :class="band.cls"
  >
    {{ band.val }}
  </span>
</template>

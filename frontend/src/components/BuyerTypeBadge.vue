<script setup lang="ts">
import { computed } from "vue";
import type { BuyerType } from "@/api/types";

const props = defineProps<{ type: BuyerType | null }>();

const LABEL: Record<BuyerType, string> = {
  importer: "Importer",
  distributor: "Distributor",
  wholesaler: "Wholesaler",
  manufacturer: "Manufacturer",
  retailer: "Retailer",
  irrelevant: "Irrelevant",
};
const meta = computed(() => {
  if (!props.type) return { label: "—", dim: true };
  return { label: LABEL[props.type], dim: props.type === "irrelevant" };
});
</script>

<template>
  <span
    class="text-[12px] font-medium"
    :class="meta.dim ? 'text-ink-300' : 'text-ink-700'"
  >
    {{ meta.label }}
  </span>
</template>

<script setup lang="ts">
defineProps<{ eyebrow?: string; title: string; subtitle?: string }>();
</script>

<template>
  <header class="border-b border-ink/8 bg-white/60 px-8 py-5 backdrop-blur">
    <div class="flex items-center justify-between gap-4">
      <div>
        <div v-if="eyebrow" class="eyebrow mb-1">{{ eyebrow }}</div>
        <h1 class="font-display text-[22px] font-semibold tracking-tight text-ink">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="mt-0.5 text-[13px] text-ink-500">{{ subtitle }}</p>
      </div>
      <div class="flex items-center gap-2">
        <slot name="actions" />
      </div>
    </div>
    <slot name="below" />
  </header>
</template>

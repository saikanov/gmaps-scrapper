<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import { useAppStore } from "@/stores/app";

const route = useRoute();
const appStore = useAppStore();

const navItems = [
  { label: "Campaigns", to: "/campaigns", icon: "pi-folder" },
];

const llmOk = computed(() => appStore.health?.llm_configured);
const sheetOk = computed(() => appStore.health?.sheet_configured);
</script>

<template>
  <div class="flex min-h-screen">
    <!-- Left rail: dark shell, the fixed home base (DESIGN.md §5.6) -->
    <aside
      class="hidden w-60 shrink-0 flex-col bg-shell text-white md:flex"
    >
      <div class="flex items-center gap-2.5 px-5 py-5">
        <span
          class="flex h-8 w-8 items-center justify-center rounded-md bg-gold font-display text-sm font-bold text-shell"
          >BF</span
        >
        <div class="leading-tight">
          <div class="font-display text-[15px] font-semibold tracking-tight">
            Buyer-Finder
          </div>
          <div class="text-[10px] uppercase tracking-[0.18em] text-ink-300">
            Trade leads
          </div>
        </div>
      </div>

      <nav class="mt-2 flex flex-col gap-1 px-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-md border-l-2 border-transparent px-3 py-2 text-sm font-medium text-white/75 transition-colors hover:bg-white/5 hover:text-white"
          :class="route.path.startsWith(item.to) && 'border-gold bg-white/5 text-gold'"
        >
          <i :class="['pi', item.icon, 'text-[15px]']" />
          {{ item.label }}
        </RouterLink>
      </nav>

      <div class="mt-auto space-y-2 px-5 py-5 text-[11px]">
        <div class="eyebrow text-ink-300">Services</div>
        <div class="flex items-center gap-2 text-white/70">
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="llmOk ? 'bg-success' : 'bg-warning'"
          />
          AI engine {{ llmOk ? "online" : "offline" }}
        </div>
        <div class="flex items-center gap-2 text-white/70">
          <span
            class="h-1.5 w-1.5 rounded-full"
            :class="sheetOk ? 'bg-success' : 'bg-danger'"
          />
          Sheet export {{ sheetOk ? "ready" : "unset" }}
        </div>
      </div>
    </aside>

    <!-- Work surface -->
    <main class="flex min-w-0 flex-1 flex-col bg-paper">
      <slot />
    </main>
  </div>
</template>

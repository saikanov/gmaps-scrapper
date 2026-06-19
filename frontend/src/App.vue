<script setup lang="ts">
import { onMounted } from "vue";
import Toast from "primevue/toast";
import ConfirmDialog from "primevue/confirmdialog";
import AppShell from "@/layouts/AppShell.vue";
import { useAppStore } from "@/stores/app";

const appStore = useAppStore();
onMounted(() => appStore.loadHealth());
</script>

<template>
  <AppShell>
    <router-view v-slot="{ Component }">
      <component :is="Component" />
    </router-view>
  </AppShell>
  <Toast position="bottom-right" />
  <ConfirmDialog />
</template>

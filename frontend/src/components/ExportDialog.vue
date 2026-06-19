<script setup lang="ts">
import { computed, ref, watch } from "vue";
import Dialog from "primevue/dialog";
import Button from "primevue/button";

const props = defineProps<{ country: string; count: number; loading?: boolean }>();
const visible = defineModel<boolean>("visible", { default: false });
const emit = defineEmits<{ (e: "confirm", sheetName: string): void }>();

const sheetName = ref("");

watch(
  () => visible.value,
  (v) => {
    if (v && !sheetName.value) sheetName.value = `(${props.country}) Lead Database`;
  },
);

const canExport = computed(() => sheetName.value.trim() && props.count > 0);
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :style="{ width: '420px' }"
    :draggable="false"
  >
    <template #header>
      <span class="font-display text-[15px] font-semibold text-ink">Export to Google Sheet</span>
    </template>

    <div class="space-y-4">
      <div>
        <label class="eyebrow mb-2 block">Sheet / tab name</label>
        <input
          v-model="sheetName"
          type="text"
          class="w-full rounded-lg border border-ink/15 bg-white px-3.5 py-2.5 text-[14px] outline-none focus:border-gold"
        />
        <p class="mt-1.5 text-[12px] text-ink-300">
          One campaign = one tab. Re-exporting appends rows.
        </p>
      </div>

      <div class="rounded-lg bg-paper px-4 py-3 text-[13px] text-ink-700">
        <span class="tnum text-[15px] font-semibold text-gold-deep">{{ count }}</span>
        leads will be written.
      </div>
    </div>

    <template #footer>
      <Button text label="Cancel" severity="secondary" @click="visible = false" />
      <Button
        label="Export"
        icon="pi pi-file-export"
        :loading="loading"
        :disabled="!canExport"
        @click="emit('confirm', sheetName.trim())"
      />
    </template>
  </Dialog>
</template>

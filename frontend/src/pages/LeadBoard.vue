<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import Select from "primevue/select";
import Skeleton from "primevue/skeleton";
import { useToast } from "primevue/usetoast";
import { useConfirm } from "primevue/useconfirm";

import PageHeader from "@/components/PageHeader.vue";
import JobProgress from "@/components/JobProgress.vue";
import ScoreBadge from "@/components/ScoreBadge.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import BuyerTypeBadge from "@/components/BuyerTypeBadge.vue";
import LeadDetailDrawer from "@/components/LeadDetailDrawer.vue";
import ExportDialog from "@/components/ExportDialog.vue";
import { api } from "@/api/client";
import { useAppStore } from "@/stores/app";
import type {
  BuyerType,
  Campaign,
  Job,
  Lead,
  LeadFilters,
  OutreachStatus,
} from "@/api/types";

const route = useRoute();
const router = useRouter();
const toast = useToast();
const confirm = useConfirm();
const appStore = useAppStore();
const id = route.params.id as string;

const campaign = ref<Campaign | null>(null);
const leads = ref<Lead[]>([]);
const jobs = ref<Job[]>([]);
const loading = ref(true);
const scoring = ref(false);
const exporting = ref(false);

const selection = ref<Lead[]>([]);
const expandedRows = ref<Record<string, boolean>>({});
const drawerLead = ref<Lead | null>(null);
const drawerOpen = ref(false);
const exportOpen = ref(false);

// --- filters (persisted to URL query) ---
const filters = reactive<LeadFilters>({
  score_gte: route.query.score ? Number(route.query.score) : null,
  type: (route.query.type as BuyerType) || null,
  city: (route.query.city as string) || null,
  status: (route.query.status as OutreachStatus) || null,
  has_email: route.query.has_email === "1" ? true : null,
});

const TYPE_OPTIONS = [
  { label: "All types", value: null },
  ...["importer", "distributor", "wholesaler", "manufacturer", "retailer"].map((v) => ({
    label: v[0].toUpperCase() + v.slice(1),
    value: v,
  })),
];
const STATUS_OPTIONS = [
  { label: "All statuses", value: null },
  ...["new", "contacted", "replied", "qualified", "rejected", "won"].map((v) => ({
    label: v[0].toUpperCase() + v.slice(1),
    value: v,
  })),
];
const SCORE_OPTIONS = [
  { label: "Any score", value: null },
  { label: "≥ 80", value: 80 },
  { label: "≥ 70", value: 70 },
  { label: "≥ 50", value: 50 },
];
const cityOptions = computed(() => {
  const set = new Set(leads.value.map((l) => l.city).filter(Boolean));
  return [{ label: "All cities", value: null }, ...[...set].sort().map((c) => ({ label: c, value: c }))];
});

const anyRunning = computed(() => campaign.value && campaign.value.jobs_running > 0);
const scoredCount = computed(() => leads.value.filter((l) => l.score !== null).length);

function syncQuery() {
  router.replace({
    query: {
      ...(filters.score_gte ? { score: String(filters.score_gte) } : {}),
      ...(filters.type ? { type: filters.type } : {}),
      ...(filters.city ? { city: filters.city } : {}),
      ...(filters.status ? { status: filters.status } : {}),
      ...(filters.has_email ? { has_email: "1" } : {}),
    },
  });
}

async function loadLeads() {
  leads.value = await api.listLeads(id, filters);
}
async function loadJobs() {
  jobs.value = await api.listJobs(id);
}
async function loadCampaign() {
  campaign.value = await api.getCampaign(id);
}

async function refreshAll() {
  await Promise.all([loadCampaign(), loadLeads(), loadJobs()]);
}

watch(
  () => ({ ...filters }),
  () => {
    syncQuery();
    loadLeads();
  },
);

// --- live polling while scraping ---
let timer: number | undefined;
function ensurePolling() {
  if (timer) return;
  timer = window.setInterval(async () => {
    await Promise.all([loadCampaign(), loadJobs()]);
    await loadLeads();
    if (!anyRunning.value) stopPolling();
  }, 6000);
}
function stopPolling() {
  if (timer) {
    clearInterval(timer);
    timer = undefined;
  }
}

async function runScoring(enrich: boolean) {
  scoring.value = true;
  try {
    const res = await api.score(id, enrich, true);
    toast.add({ severity: "success", summary: "Scoring complete", detail: res.detail, life: 3000 });
    await loadLeads();
  } catch (e: any) {
    toast.add({ severity: "error", summary: "Scoring failed", detail: e?.message, life: 4000 });
  } finally {
    scoring.value = false;
  }
}

// optimistic outreach status update + rollback
async function setStatus(lead: Lead, status: OutreachStatus) {
  const prev = lead.outreach_status;
  lead.outreach_status = status;
  if (drawerLead.value?.id === lead.id) drawerLead.value = { ...lead };
  try {
    await api.updateLead(lead.id, status);
  } catch (e: any) {
    lead.outreach_status = prev;
    toast.add({ severity: "error", summary: "Could not update status", life: 3000 });
  }
}

async function bulkStatus(status: OutreachStatus) {
  const targets = [...selection.value];
  await Promise.all(targets.map((l) => setStatus(l, status)));
  toast.add({ severity: "success", summary: `${targets.length} set to ${status}`, life: 2500 });
}

function openExport() {
  if (!appStore.health?.sheet_configured) {
    toast.add({
      severity: "warn",
      summary: "Sheet export not configured",
      detail: "Set GOOGLE_SHEET_WEB_APP_URL on the backend.",
      life: 4000,
    });
    return;
  }
  exportOpen.value = true;
}

const exportCount = computed(() => (selection.value.length ? selection.value.length : leads.value.length));

async function doExport(sheetName: string) {
  exporting.value = true;
  try {
    const body: any = { sheet_name: sheetName };
    if (selection.value.length) body.lead_ids = selection.value.map((l) => l.id);
    else if (filters.score_gte) body.score_gte = filters.score_gte;
    const res = await api.exportSheet(id, body);
    toast.add({ severity: "success", summary: "Exported to Sheet", detail: res.detail, life: 3500 });
    exportOpen.value = false;
    selection.value = [];
  } catch (e: any) {
    toast.add({
      severity: "error",
      summary: "Export failed",
      detail: e?.response?.data?.detail ?? e?.message,
      life: 4500,
    });
  } finally {
    exporting.value = false;
  }
}

function openDrawer(lead: Lead) {
  drawerLead.value = lead;
  drawerOpen.value = true;
}

onMounted(async () => {
  loading.value = true;
  try {
    await refreshAll();
    if (anyRunning.value) ensurePolling();
  } finally {
    loading.value = false;
  }
});
onUnmounted(stopPolling);
</script>

<template>
  <PageHeader
    eyebrow="Lead board"
    :title="campaign?.commodity ?? 'Leads'"
    :subtitle="campaign ? `${campaign.country} · ${leads.length} leads` : ''"
  >
    <template #actions>
      <Button
        text
        severity="secondary"
        icon="pi pi-sliders-h"
        label="Keywords"
        @click="router.push(`/campaigns/${id}/keywords`)"
      />
      <Button
        outlined
        :label="scoredCount ? 'Re-score' : 'Run AI scoring'"
        icon="pi pi-sparkles"
        :loading="scoring"
        :disabled="!appStore.health?.llm_configured || leads.length === 0"
        @click="runScoring(false)"
      />
      <Button label="Export" icon="pi pi-file-export" @click="openExport" />
    </template>
  </PageHeader>

  <section class="flex-1 overflow-auto px-8 py-5">
    <!-- live scraping progress -->
    <div v-if="jobs.length" class="mb-4">
      <JobProgress :jobs="jobs" />
    </div>

    <!-- filter bar -->
    <div class="mb-3 flex flex-wrap items-center gap-2 rounded-card border border-ink/8 bg-white px-4 py-2.5 shadow-card">
      <span class="eyebrow mr-1">Filters</span>
      <Select v-model="filters.score_gte" :options="SCORE_OPTIONS" optionLabel="label" optionValue="value" class="w-32" />
      <Select v-model="filters.type" :options="TYPE_OPTIONS" optionLabel="label" optionValue="value" class="w-40" />
      <Select v-model="filters.city" :options="cityOptions" optionLabel="label" optionValue="value" class="w-40" filter />
      <Select v-model="filters.status" :options="STATUS_OPTIONS" optionLabel="label" optionValue="value" class="w-40" />
      <label class="ml-1 flex cursor-pointer items-center gap-1.5 text-[13px] text-ink-700">
        <input type="checkbox" :checked="filters.has_email === true" class="h-4 w-4 accent-gold" @change="filters.has_email = ($event.target as HTMLInputElement).checked ? true : null" />
        Has email
      </label>
      <div class="ml-auto flex items-center gap-2">
        <span v-if="selection.length" class="text-[12px] text-ink-500">{{ selection.length }} selected</span>
        <Button v-if="selection.length" text size="small" label="Mark contacted" icon="pi pi-check" @click="bulkStatus('contacted')" />
      </div>
    </div>

    <!-- loading -->
    <div v-if="loading" class="rounded-card border border-ink/8 bg-white p-4 shadow-card">
      <Skeleton v-for="n in 8" :key="n" height="2.4rem" class="mb-2" />
    </div>

    <!-- empty -->
    <div
      v-else-if="leads.length === 0"
      class="mx-auto mt-12 max-w-md rounded-card border border-dashed border-ink/15 bg-white px-8 py-12 text-center"
    >
      <div class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-paper text-ink-300">
        <i class="pi pi-inbox text-xl" />
      </div>
      <h3 class="font-display text-lg font-semibold text-ink">
        {{ anyRunning ? "Scraping… leads will appear here" : "No leads yet" }}
      </h3>
      <p class="mt-1 text-sm text-ink-500">
        {{ anyRunning ? "The scraper is working through your queries." : "Dispatch keywords to start finding buyers." }}
      </p>
      <Button
        v-if="!anyRunning"
        class="mt-5"
        label="Go to keywords"
        icon="pi pi-arrow-right"
        @click="router.push(`/campaigns/${id}/keywords`)"
      />
    </div>

    <!-- table -->
    <div v-else class="overflow-hidden rounded-card border border-ink/8 bg-white shadow-card">
      <DataTable
        v-model:selection="selection"
        v-model:expandedRows="expandedRows"
        :value="leads"
        dataKey="id"
        paginator
        :rows="25"
        :rowsPerPageOptions="[25, 50, 100]"
        removableSort
        rowHover
        class="text-[13px]"
      >
        <Column selectionMode="multiple" headerStyle="width:2.5rem" />
        <Column expander headerStyle="width:2.5rem" />
        <Column field="name" header="Company" sortable>
          <template #body="{ data }">
            <button class="text-left font-medium text-ink hover:text-gold-deep" @click="openDrawer(data)">
              {{ data.name }}
              <span class="block text-[11px] font-normal text-ink-300">{{ data.category }}</span>
            </button>
          </template>
        </Column>
        <Column field="lead_type" header="Type" sortable>
          <template #body="{ data }"><BuyerTypeBadge :type="data.lead_type" /></template>
        </Column>
        <Column field="score" header="Score" sortable>
          <template #body="{ data }"><ScoreBadge :score="data.score" /></template>
        </Column>
        <Column field="city" header="City" sortable>
          <template #body="{ data }"><span class="text-ink-700">{{ data.city || "—" }}</span></template>
        </Column>
        <Column header="Contact">
          <template #body="{ data }">
            <div class="flex items-center gap-2 text-ink-300">
              <i class="pi pi-phone text-[12px]" :class="data.phone && 'text-gold-deep'" v-tooltip.top="data.phone || 'no phone'" />
              <i class="pi pi-envelope text-[12px]" :class="data.email && 'text-gold-deep'" v-tooltip.top="data.email || 'no email'" />
              <i class="pi pi-globe text-[12px]" :class="data.website && 'text-gold-deep'" v-tooltip.top="data.website || 'no website'" />
            </div>
          </template>
        </Column>
        <Column field="outreach_status" header="Status" sortable>
          <template #body="{ data }"><StatusBadge :status="data.outreach_status" /></template>
        </Column>

        <template #expansion="{ data }">
          <div class="grid gap-4 bg-paper/60 px-6 py-4 md:grid-cols-2">
            <div>
              <div class="eyebrow mb-1">AI reasoning</div>
              <p class="text-[13px] text-ink-700">{{ data.score_reason || "Not scored yet." }}</p>
              <div v-if="data.enrichment?.summary" class="mt-3">
                <div class="eyebrow mb-1 text-gold-deep">Enrichment</div>
                <p class="text-[13px] text-ink-700">{{ data.enrichment.summary }}</p>
              </div>
            </div>
            <div class="space-y-1.5 text-[13px]">
              <div><span class="text-ink-300">Phone:</span> <span class="tnum">{{ data.phone || "—" }}</span></div>
              <div><span class="text-ink-300">Email:</span> {{ data.email || "—" }}</div>
              <div>
                <span class="text-ink-300">Website:</span>
                <a v-if="data.website" :href="data.website" target="_blank" class="text-gold-deep hover:underline">{{ data.website }}</a>
                <span v-else>—</span>
              </div>
              <div class="pt-1">
                <Button text size="small" label="Open detail" icon="pi pi-external-link" @click="openDrawer(data)" />
              </div>
            </div>
          </div>
        </template>
      </DataTable>
    </div>
  </section>

  <LeadDetailDrawer
    v-model:visible="drawerOpen"
    :lead="drawerLead"
    @setStatus="(s) => drawerLead && setStatus(drawerLead, s)"
  />
  <ExportDialog
    v-model:visible="exportOpen"
    :country="campaign?.country ?? ''"
    :count="exportCount"
    :loading="exporting"
    @confirm="doExport"
  />
</template>

import axios from "axios";
import type {
  Campaign,
  Health,
  Job,
  KeywordPlan,
  Lead,
  LeadFilters,
  OutreachStatus,
} from "./types";

const http = axios.create({ baseURL: "/api", timeout: 180_000 });

export const api = {
  health: () => http.get<Health>("/health").then((r) => r.data),

  // Campaigns
  listCampaigns: () => http.get<Campaign[]>("/campaigns").then((r) => r.data),
  getCampaign: (id: string) =>
    http.get<Campaign>(`/campaigns/${id}`).then((r) => r.data),
  createCampaign: (body: {
    commodity: string;
    country: string;
    buyer_profile: string[];
    keyword_mode: string;
  }) => http.post<Campaign>("/campaigns", body).then((r) => r.data),

  // Keywords (AI #1)
  generateKeywords: (id: string) =>
    http.post<KeywordPlan>(`/campaigns/${id}/keywords`).then((r) => r.data),
  getKeywords: (id: string) =>
    http.get<KeywordPlan>(`/campaigns/${id}/keywords`).then((r) => r.data),

  // Dispatch + jobs
  dispatch: (
    id: string,
    queries: { query: string; city: string; tier: number; lang?: string }[],
  ) =>
    http
      .post(`/campaigns/${id}/dispatch`, { queries })
      .then((r) => r.data),
  listJobs: (id: string) =>
    http.get<Job[]>(`/campaigns/${id}/jobs`).then((r) => r.data),

  // Scoring + enrichment (AI #2)
  score: (id: string, enrich = false, only_unscored = true) =>
    http
      .post(`/campaigns/${id}/score`, { enrich, only_unscored })
      .then((r) => r.data),

  // Leads
  listLeads: (id: string, filters: LeadFilters = {}) =>
    http
      .get<Lead[]>(`/campaigns/${id}/leads`, {
        params: cleanParams(filters as Record<string, unknown>),
      })
      .then((r) => r.data),
  updateLead: (leadId: string, outreach_status: OutreachStatus) =>
    http
      .patch<Lead>(`/leads/${leadId}`, { outreach_status })
      .then((r) => r.data),

  // Export
  exportSheet: (
    id: string,
    body: {
      sheet_name?: string;
      score_gte?: number | null;
      lead_ids?: string[];
    },
  ) => http.post(`/campaigns/${id}/export`, body).then((r) => r.data),
};

function cleanParams(obj: Record<string, unknown>) {
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj)) {
    if (v !== null && v !== undefined && v !== "") out[k] = v;
  }
  return out;
}

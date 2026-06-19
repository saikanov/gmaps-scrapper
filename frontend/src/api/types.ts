export type BuyerType =
  | "importer"
  | "distributor"
  | "wholesaler"
  | "manufacturer"
  | "retailer"
  | "irrelevant";

export type OutreachStatus =
  | "new"
  | "contacted"
  | "replied"
  | "qualified"
  | "rejected"
  | "won";

export interface Campaign {
  id: string;
  commodity: string;
  country: string;
  buyer_profile: string;
  keyword_mode: "tiering" | "all_at_once";
  created_at: string;
  lead_count: number;
  job_count: number;
  jobs_running: number;
  jobs_done: number;
  has_keywords: boolean;
}

export interface KeywordCity {
  name: string;
  tier: number;
  reason: string;
}
export interface KeywordQuery {
  query: string;
  city: string;
  tier: number;
}
export interface KeywordPlan {
  language: string;
  buyer_terms: string[];
  commodity_terms: string[];
  cities: KeywordCity[];
  queries: KeywordQuery[];
}

export interface Job {
  id: string;
  query: string;
  city: string;
  tier: number;
  lang: string;
  status: string;
  leads_found: number;
  error: string | null;
  dispatched_at: string | null;
  created_at: string;
}

export interface Lead {
  id: string;
  campaign_id: string;
  name: string;
  category: string;
  address: string;
  city: string;
  phone: string;
  email: string;
  website: string;
  gmaps_url: string;
  latitude: number | null;
  longitude: number | null;
  place_id: string;
  review_count: number;
  review_rating: number | null;
  score: number | null;
  lead_type: BuyerType | null;
  score_reason: string | null;
  enrichment: Record<string, any> | null;
  enriched: boolean;
  outreach_status: OutreachStatus;
  provenance: { query: string; city: string }[] | null;
  created_at: string;
}

export interface Health {
  status: string;
  llm_configured: boolean;
  llm_model: string | null;
  sheet_configured: boolean;
  enrichment_threshold: number;
}

export interface LeadFilters {
  score_gte?: number | null;
  type?: BuyerType | null;
  city?: string | null;
  status?: OutreachStatus | null;
  has_email?: boolean | null;
}

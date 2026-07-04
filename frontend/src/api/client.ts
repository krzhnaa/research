// frontend/src/api/client.ts
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 120000, // crawling + AI can take a while
});

export interface CompanyInfo {
  company_name: string;
  website: string;
  phone: string | null;
  address: string | null;
  products_services: string[];
  pain_points: string[];
  summary: string;
  industry: string | null;
  confidence?: Record<string, string>;
  sources?: Record<string, string>;
  page_sources?: Record<string, string>;
}

export interface Competitor {
  name: string;
  website: string;
}

export interface CrawledPage {
  url: string;
  title: string;
  content: string;
  category: string;
}

export interface CrawlMetadata {
  pages_found: number;
  pages_crawled: number;
  used_sitemap: boolean;
  structured_data_found: boolean;
  javascript_site_detected: boolean;
  crawl_notes: string[];
}

export interface ResearchTiming {
  crawl_seconds: number;
  total_seconds: number;
}

export interface ResearchResult {
  company: CompanyInfo;
  competitors: Competitor[];
  crawled_pages: CrawledPage[];
  crawl_metadata: CrawlMetadata;
  sources: Record<string, string>;
  timing: ResearchTiming;
  model_used: string | null;
}

export async function researchCompany(input: string, model: string): Promise<ResearchResult> {
  const res = await api.post<ResearchResult>("/research", { input, model });
  return res.data;
}

export async function downloadPdf(result: ResearchResult): Promise<Blob> {
  const res = await api.post("/pdf", result, { responseType: "blob" });
  return res.data;
}

export async function sendToDiscord(
  botToken: string,
  channelId: string,
  applicant: { name: string; email: string },
  result: ResearchResult
) {
  const res = await api.post("/discord/send", {
    bot_token: botToken,
    channel_id: channelId,
    applicant,
    result,
  });
  return res.data;
}
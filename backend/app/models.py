# backend/app/models.py
from pydantic import BaseModel, Field
from typing import Optional


class ResearchRequest(BaseModel):
    input: str          # company name OR website URL
    model: Optional[str] = None  # OpenRouter model id, optional


class Competitor(BaseModel):
    name: str
    website: str


class CompanyInfo(BaseModel):
    company_name: str
    website: str
    phone: Optional[str] = None
    address: Optional[str] = None
    products_services: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    summary: str = ""
    industry: Optional[str] = None
    confidence: dict[str, str] = Field(default_factory=dict)
    sources: dict[str, str] = Field(default_factory=dict)
    page_sources: dict[str, str] = Field(default_factory=dict)


class CrawledPage(BaseModel):
    url: str
    title: str
    content: str
    category: str


class CrawlMetadata(BaseModel):
    pages_found: int = 0
    pages_crawled: int = 0
    used_sitemap: bool = False
    structured_data_found: bool = False
    javascript_site_detected: bool = False
    crawl_notes: list[str] = Field(default_factory=list)


class ResearchTiming(BaseModel):
    crawl_seconds: float = 0.0
    total_seconds: float = 0.0


class ResearchResult(BaseModel):
    company: CompanyInfo
    competitors: list[Competitor] = Field(default_factory=list)
    crawled_pages: list[CrawledPage] = Field(default_factory=list)
    crawl_metadata: CrawlMetadata = Field(default_factory=CrawlMetadata)
    sources: dict[str, str] = Field(default_factory=dict)
    timing: ResearchTiming = Field(default_factory=ResearchTiming)
    model_used: Optional[str] = None


class ApplicantInfo(BaseModel):
    name: str
    email: str


class DiscordConfig(BaseModel):
    bot_token: str
    channel_id: str


class DiscordSendRequest(BaseModel):
    applicant: ApplicantInfo
    company_name: str
    company_website: str
    pdf_base64: str  # PDF sent as base64 string from frontend, or generated server-side

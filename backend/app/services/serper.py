# backend/app/services/serper.py
import time
from urllib.parse import urlparse

import httpx

from app.config import settings

SERPER_URL = "https://google.serper.dev/search"
CACHE_TTL_SECONDS = 600
_SEARCH_CACHE: dict[str, tuple[float, list[dict]]] = {}

BLOCKED_DOMAINS = [
    "wikipedia.org",
    "linkedin.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "instagram.com",
    "crunchbase.com",
    "youtube.com",
    "glassdoor.com",
    "indeed.com",
    "bloomberg.com",
]


def _get_cached(query: str) -> list[dict] | None:
    cached = _SEARCH_CACHE.get(query)
    if not cached:
        return None
    cached_at, payload = cached
    if time.time() - cached_at > CACHE_TTL_SECONDS:
        _SEARCH_CACHE.pop(query, None)
        return None
    return payload


def _set_cache(query: str, results: list[dict]) -> None:
    _SEARCH_CACHE[query] = (time.time(), results)


async def serper_search(query: str, num: int = 8) -> list[dict]:
    """Raw Serper.dev search call with short-lived in-memory caching to protect free-tier quota."""
    if not settings.SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is not set")

    cached = _get_cached(query)
    if cached is not None:
        return cached

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(
            SERPER_URL,
            json={"q": query, "num": num},
            headers={
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
        )
        res.raise_for_status()
        data = res.json()
        organic = data.get("organic", [])
        _set_cache(query, organic)
        return organic


async def resolve_company_website(company_name: str) -> str | None:
    """Given a company name, find its most likely official website."""
    results = await serper_search(f"{company_name} official website", num=5)

    for result in results:
        link = result.get("link")
        if not link:
            continue
        try:
            host = (urlparse(link).hostname or "").replace("www.", "")
        except Exception:
            continue

        if not any(blocked in host for blocked in BLOCKED_DOMAINS):
            parsed = urlparse(link)
            return f"{parsed.scheme}://{parsed.netloc}"

    return None


async def search_public_info(query: str) -> list[dict]:
    """Generic search helper for gathering contact info / public data."""
    return await serper_search(query, num=8)


async def search_competitors(company_name: str, industry: str) -> list[dict]:
    """Search for competitors operating in the same industry."""
    query = f"top competitors of {company_name} in {industry} industry"
    return await serper_search(query, num=8)


async def verify_contact_info(company_name: str, website: str) -> list[dict]:
    """Cross-check missing contact fields using search snippets as a secondary source."""
    domain = (urlparse(website).hostname or website).replace("www.", "")
    query = f'"{company_name}" "{domain}" phone number address'
    results = await serper_search(query, num=5)
    snippets: list[dict] = []
    for result in results:
        snippets.append(
            {
                "title": result.get("title", ""),
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
            }
        )
    return snippets


async def verify_competitor_relevance(company_name: str, competitor_name: str, industry: str) -> bool:
    """Sanity-check AI-proposed competitors so obviously unrelated names are filtered out."""
    query = f'"{competitor_name}" "{industry}" competitor of "{company_name}"'
    results = await serper_search(query, num=5)
    if not results:
        return False

    haystacks = [
        f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        for result in results
    ]
    competitor_lower = competitor_name.lower()
    industry_tokens = [token for token in industry.lower().split() if len(token) > 3]
    return any(
        competitor_lower in haystack and any(token in haystack for token in industry_tokens)
        for haystack in haystacks
    )

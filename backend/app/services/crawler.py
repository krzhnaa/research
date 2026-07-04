import asyncio
import re
import time
from urllib import robotparser
from urllib.parse import urljoin, urlparse, urlunparse
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup

TARGET_PATHS = [
    "/",
    "/about",
    "/about-us",
    "/products",
    "/product",
    "/services",
    "/solutions",
    "/contact",
    "/contact-us",
    "/pricing",
    "/plans",
]
PAGE_CATEGORY_PATTERNS = {
    "home": ["/", "home"],
    "about": ["about", "about-us", "company", "who-we-are"],
    "products": ["product", "products", "features", "platform"],
    "services": ["service", "services", "solution", "solutions"],
    "pricing": ["pricing", "plans", "plan", "subscription"],
    "contact": ["contact", "contact-us", "get-in-touch", "reach-us"],
}
PRIORITY_KEYWORDS = ["pricing", "product", "service", "solution", "about", "contact", "home"]
IGNORE_KEYWORDS = [
    "login",
    "signin",
    "sign-in",
    "signup",
    "sign-up",
    "register",
    "cart",
    "checkout",
    "privacy",
    "terms",
    "cookie",
    "career",
    "careers",
    "job",
    "jobs",
    "blog/",
]
TRACKING_QUERY_PREFIXES = ("utm_", "fbclid", "gclid", "mc_", "ref")
PHONE_REGEX = re.compile(r"(?:(?:\+?\d{1,3}[\s().-]*)?(?:\d[\s().-]*){7,}\d)")
EMAIL_REGEX = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    cleaned_path = parsed.path.rstrip("/") or "/"
    normalized = parsed._replace(query="", fragment="", path=cleaned_path)
    return urlunparse(normalized)


def is_ignored_url(url: str) -> bool:
    lower = url.lower()
    if any(bad in lower for bad in IGNORE_KEYWORDS):
        return True
    parsed = urlparse(lower)
    if any(key.lower().startswith(TRACKING_QUERY_PREFIXES) for key, _ in []):
        return True
    return False


def category_rank(category: str) -> int:
    order = {
        "home": 7,
        "about": 6,
        "products": 5,
        "services": 4,
        "pricing": 3,
        "contact": 2,
        "other": 1,
    }
    return order.get(category, 0)


async def fetch_html(url: str, client: httpx.AsyncClient) -> str | None:
    try:
        res = await client.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        content_type = res.headers.get("content-type", "").lower()
        if res.status_code == 200 and (
            "text/html" in content_type
            or "application/xhtml+xml" in content_type
            or "<html" in res.text.lower()
        ):
            return res.text
    except Exception:
        return None
    return None


async def fetch_text(url: str, client: httpx.AsyncClient) -> str | None:
    try:
        res = await client.get(url, headers=HEADERS, timeout=10, follow_redirects=True)
        if res.status_code == 200:
            return res.text
    except Exception:
        return None
    return None


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "svg", "noscript"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:5000]


def extract_title(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    return ""


def extract_heading(html: str) -> str:
    soup = BeautifulSoup(html, "lxml")
    for tag_name in ("h1", "h2"):
        tag = soup.find(tag_name)
        if tag:
            heading = tag.get_text(" ", strip=True)
            if heading:
                return heading
    return ""


def detect_page_category(url: str, title: str = "", heading: str = "") -> str:
    parsed = urlparse(url)
    path = parsed.path.lower().strip("/") or "/"
    haystack = f"{path} {title.lower()} {heading.lower()}"

    if path in {"", "/"}:
        return "home"

    for category, patterns in PAGE_CATEGORY_PATTERNS.items():
        if any(pattern in haystack for pattern in patterns if pattern != "/"):
            return category
    return "other"


def extract_structured_data(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    payloads: list[dict] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = (tag.string or tag.get_text() or "").strip()
        if not raw:
            continue
        try:
            import json

            parsed = json.loads(raw)
        except Exception:
            continue
        items = parsed if isinstance(parsed, list) else [parsed]
        for item in items:
            if isinstance(item, dict):
                payloads.append(item)
    return payloads


def summarize_structured_data(payloads: list[dict]) -> dict:
    summary = {
        "company_name": None,
        "phone": None,
        "address": None,
        "emails": [],
        "same_as": [],
        "logo": None,
        "raw": payloads,
    }
    for payload in payloads:
        graph_items = payload.get("@graph") if isinstance(payload.get("@graph"), list) else [payload]
        for item in graph_items:
            if not isinstance(item, dict):
                continue
            item_type = item.get("@type")
            types = item_type if isinstance(item_type, list) else [item_type]
            if any(t in {"Organization", "Corporation", "LocalBusiness", "WebSite"} for t in types):
                summary["company_name"] = summary["company_name"] or item.get("name")
                summary["phone"] = summary["phone"] or item.get("telephone")
                summary["logo"] = summary["logo"] or item.get("logo")
                if isinstance(item.get("sameAs"), list):
                    summary["same_as"] = list(dict.fromkeys(summary["same_as"] + item["sameAs"]))
                address = item.get("address")
                if isinstance(address, dict):
                    parts = [
                        address.get("streetAddress"),
                        address.get("addressLocality"),
                        address.get("addressRegion"),
                        address.get("postalCode"),
                        address.get("addressCountry"),
                    ]
                    summary["address"] = summary["address"] or ", ".join(part for part in parts if part)
                email = item.get("email")
                if email:
                    summary["emails"].append(email)
    summary["emails"] = list(dict.fromkeys(summary["emails"]))
    return summary


def extract_contacts(text: str) -> dict:
    phones = []
    for match in PHONE_REGEX.findall(text):
        candidate = re.sub(r"\s+", " ", match).strip(" .,-")
        digits = re.sub(r"\D", "", candidate)
        if len(digits) >= 7:
            phones.append(candidate)
    emails = [email.lower() for email in EMAIL_REGEX.findall(text)]
    return {
        "phones": list(dict.fromkeys(phones))[:10],
        "emails": list(dict.fromkeys(emails))[:10],
    }


def discover_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = set()
    base_parsed = urlparse(base_url)
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        if parsed.netloc != base_parsed.netloc:
            continue
        clean_url = normalize_url(full_url)
        if is_ignored_url(clean_url):
            continue
        links.add(clean_url)
    return list(links)


def score_link(url: str) -> int:
    lower = url.lower()
    for index, keyword in enumerate(PRIORITY_KEYWORDS):
        if keyword in lower:
            return len(PRIORITY_KEYWORDS) - index
    return 0


def build_target_urls(base_url: str) -> list[str]:
    base = base_url.rstrip("/")
    return [normalize_url(f"{base}{path}") for path in TARGET_PATHS]


async def fetch_sitemap_urls(base_url: str, client: httpx.AsyncClient) -> list[str]:
    sitemap_url = urljoin(base_url.rstrip("/") + "/", "sitemap.xml")
    try:
        sitemap_xml = await fetch_text(sitemap_url, client)
        if not sitemap_xml:
            return []
        root = ElementTree.fromstring(sitemap_xml)
    except Exception:
        return []

    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}")[0] + "}"

    urls: list[str] = []
    if root.tag.endswith("sitemapindex"):
        for sitemap in root.findall(f".//{namespace}loc")[:3]:
            try:
                nested_xml = await fetch_text(sitemap.text.strip(), client) if sitemap.text else None
                if not nested_xml:
                    continue
                nested_root = ElementTree.fromstring(nested_xml)
                nested_namespace = ""
                if nested_root.tag.startswith("{"):
                    nested_namespace = nested_root.tag.split("}")[0] + "}"
                for loc in nested_root.findall(f".//{nested_namespace}loc"):
                    if loc.text:
                        normalized = normalize_url(loc.text.strip())
                        if not is_ignored_url(normalized):
                            urls.append(normalized)
            except Exception:
                continue
    else:
        for loc in root.findall(f".//{namespace}loc"):
            if loc.text:
                normalized = normalize_url(loc.text.strip())
                if not is_ignored_url(normalized):
                    urls.append(normalized)
    return list(dict.fromkeys(urls))


async def build_robot_parser(base_url: str, client: httpx.AsyncClient) -> robotparser.RobotFileParser | None:
    robots_url = urljoin(base_url.rstrip("/") + "/", "robots.txt")
    try:
        robots_text = await fetch_text(robots_url, client)
        if not robots_text:
            return None
        parser = robotparser.RobotFileParser()
        parser.set_url(robots_url)
        parser.parse(robots_text.splitlines())
        return parser
    except Exception:
        return None


async def crawl_website(base_url: str, max_pages: int = 15, time_budget_seconds: int = 25) -> dict:
    """
    Crawl important pages with broad source coverage and bounded concurrency.
    Uses guessed high-value paths, homepage link discovery, sitemap discovery, and robots-aware fetching.
    """
    normalized_base = normalize_url(base_url)
    visited: set[str] = set()
    results: list[dict] = []
    crawl_notes: list[str] = []
    found_urls: list[str] = []
    same_host_urls: list[str] = []
    used_sitemap = False
    structured_payloads: list[dict] = []
    extracted_contacts = {"phones": [], "emails": []}
    started_at = time.perf_counter()
    seen_content_signatures: set[str] = set()
    category_counts: dict[str, int] = {}

    async def fetch_page_candidate(
        url: str,
        client: httpx.AsyncClient,
        semaphore: asyncio.Semaphore,
        robot_rules: robotparser.RobotFileParser | None,
    ) -> dict | None:
        try:
            if time.perf_counter() - started_at > time_budget_seconds:
                return None
            if robot_rules and not robot_rules.can_fetch(HEADERS["User-Agent"], url):
                crawl_notes.append(f"Skipped {url} due to robots.txt restrictions.")
                return None
            async with semaphore:
                html = await fetch_html(url, client)
            if not html:
                return None

            text = extract_text(html)
            if len(text) < 50:
                return None
            if len(text) < 200:
                crawl_notes.append(f"Low-text page detected at {url}; content may be JS-rendered or sparse.")

            title = extract_title(html)
            heading = extract_heading(html)
            category = detect_page_category(url, title, heading)
            payloads = extract_structured_data(html)
            contacts = extract_contacts(text)
            signature = re.sub(r"\s+", " ", text[:1200]).strip().lower()
            discovered_links = discover_links(html, url)

            return {
                "url": url,
                "title": title,
                "heading": heading,
                "content": text,
                "category": category,
                "structured_payloads": payloads,
                "contacts": contacts,
                "signature": signature,
                "discovered_links": discovered_links,
            }
        except Exception:
            return None

    async with httpx.AsyncClient() as client:
        robot_rules = await build_robot_parser(normalized_base, client)
        homepage_html = await fetch_html(normalized_base, client)
        if not homepage_html:
            return {
                "pages": [],
                "crawl_metadata": {
                    "pages_found": 0,
                    "pages_crawled": 0,
                    "used_sitemap": False,
                    "structured_data_found": False,
                    "javascript_site_detected": False,
                    "crawl_notes": ["Homepage HTML could not be fetched."],
                },
                "structured_data": {},
                "contact_signals": extracted_contacts,
            }

        homepage_text = extract_text(homepage_html)
        if len(homepage_text) < 200:
            crawl_notes.append(
                "Homepage content is very thin after HTML cleanup; the site may rely on client-side rendering."
            )

        homepage_title = extract_title(homepage_html)
        homepage_heading = extract_heading(homepage_html)
        payloads = extract_structured_data(homepage_html)
        structured_payloads.extend(payloads)
        homepage_contacts = extract_contacts(homepage_text)
        extracted_contacts["phones"].extend(homepage_contacts["phones"])
        extracted_contacts["emails"].extend(homepage_contacts["emails"])

        homepage_signature = re.sub(r"\s+", " ", homepage_text[:1200]).strip().lower()
        seen_content_signatures.add(homepage_signature)
        visited.add(normalized_base)
        results.append(
            {
                "url": normalized_base,
                "title": homepage_title,
                "content": homepage_text,
                "category": detect_page_category(normalized_base, homepage_title, homepage_heading),
            }
        )
        category_counts[results[0]["category"]] = 1

        discovered_links = discover_links(homepage_html, normalized_base)
        sitemap_links = await fetch_sitemap_urls(normalized_base, client)
        guessed_links = build_target_urls(normalized_base)

        if sitemap_links:
            used_sitemap = True
            found_urls.extend(sitemap_links)
        found_urls.extend(discovered_links)
        found_urls.extend(guessed_links)

        base_host = urlparse(normalized_base).netloc
        for candidate in found_urls:
            try:
                normalized_candidate = normalize_url(candidate)
                if urlparse(normalized_candidate).netloc == base_host and not is_ignored_url(normalized_candidate):
                    same_host_urls.append(normalized_candidate)
            except Exception:
                continue

        ranked_urls = sorted(
            set(same_host_urls),
            key=lambda candidate: (
                category_rank(detect_page_category(candidate)),
                score_link(candidate),
                -len(candidate),
            ),
            reverse=True,
        )

        semaphore = asyncio.Semaphore(4)
        queued_urls = [url for url in ranked_urls if url not in visited][: max_pages * 3]
        async def process_candidates(candidates: list[str]) -> list[str]:
            nested_candidates: list[str] = []
            fetch_tasks = [
                fetch_page_candidate(url, client, semaphore, robot_rules)
                for url in candidates
            ]
            fetched_pages = await asyncio.gather(*fetch_tasks, return_exceptions=True)

            for page in fetched_pages:
                if len(results) >= max_pages:
                    break
                if time.perf_counter() - started_at > time_budget_seconds:
                    crawl_notes.append(f"Stopped crawling after reaching the {time_budget_seconds}s time budget.")
                    break
                if not isinstance(page, dict):
                    continue
                try:
                    url = page["url"]
                    if url in visited:
                        continue
                    visited.add(url)

                    signature = page.get("signature", "")
                    if signature and signature in seen_content_signatures:
                        crawl_notes.append(f"Skipped duplicate content at {url}.")
                        continue
                    if signature:
                        seen_content_signatures.add(signature)

                    category = page.get("category", "other")
                    if category != "other" and category_counts.get(category, 0) >= 2:
                        continue

                    category_counts[category] = category_counts.get(category, 0) + 1
                    structured_payloads.extend(page.get("structured_payloads", []))
                    contacts = page.get("contacts", {})
                    extracted_contacts["phones"].extend(contacts.get("phones", []))
                    extracted_contacts["emails"].extend(contacts.get("emails", []))

                    results.append(
                        {
                            "url": url,
                            "title": page.get("title", ""),
                            "content": page.get("content", ""),
                            "category": category,
                        }
                    )
                    nested_candidates.extend(page.get("discovered_links", []))
                except Exception:
                    continue
            return nested_candidates

        nested_links = await process_candidates(queued_urls)

        if len(results) < max_pages and time.perf_counter() - started_at <= time_budget_seconds:
            ranked_nested = sorted(
                {
                    normalize_url(link)
                    for link in nested_links
                    if urlparse(normalize_url(link)).netloc == base_host
                    and not is_ignored_url(normalize_url(link))
                    and normalize_url(link) not in visited
                },
                key=lambda candidate: (
                    category_rank(detect_page_category(candidate)),
                    score_link(candidate),
                    -len(candidate),
                ),
                reverse=True,
            )
            await process_candidates(ranked_nested[: max_pages * 2])

    extracted_contacts["phones"] = list(dict.fromkeys(extracted_contacts["phones"]))[:10]
    extracted_contacts["emails"] = list(dict.fromkeys(extracted_contacts["emails"]))[:10]
    structured_summary = summarize_structured_data(structured_payloads)

    return {
        "pages": results,
        "crawl_metadata": {
            "pages_found": len(set(same_host_urls)),
            "pages_crawled": len(results),
            "used_sitemap": used_sitemap,
            "structured_data_found": bool(structured_payloads),
            "javascript_site_detected": any(
                "JS-rendered" in note or "client-side rendering" in note for note in crawl_notes
            ),
            "crawl_notes": crawl_notes,
        },
        "structured_data": structured_summary,
        "contact_signals": extracted_contacts,
    }

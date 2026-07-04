# backend/app/services/openrouter.py
import json
import re
from typing import Any

import httpx
from pydantic import BaseModel, Field, ValidationError

from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Confirmed-live free models, tried in order until one works
MODEL_CHAIN = [
    "openai/gpt-oss-120b:free",
    "openai/gpt-oss-20b:free",
    "z-ai/glm-4.5-air:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]


class AnalysisResponseModel(BaseModel):
    summary: str
    industry: str | None = None
    products_services: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    phone: str | None = None
    address: str | None = None
    competitors: list[str] = Field(default_factory=list)
    confidence: dict[str, str] = Field(default_factory=dict)
    sources: dict[str, str] = Field(default_factory=dict)
    page_sources: dict[str, str] = Field(default_factory=dict)


async def call_openrouter(prompt: str, model: str | None = None) -> tuple[str, str]:
    chain = [model] + [candidate for candidate in MODEL_CHAIN if candidate != model] if model else MODEL_CHAIN
    last_error = None

    async with httpx.AsyncClient(timeout=60) as client:
        for candidate in chain:
            try:
                res = await client.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": candidate,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                    },
                )

                if res.status_code == 429:
                    print(f"[OpenRouter] {candidate} rate-limited, trying next model...")
                    last_error = f"{candidate}: 429 rate limited"
                    continue

                if res.status_code == 404:
                    print(f"[OpenRouter] {candidate} not found, trying next model...")
                    last_error = f"{candidate}: 404 not found"
                    continue

                if res.status_code != 200:
                    last_error = f"{candidate}: {res.status_code} {res.text[:200]}"
                    continue

                data = res.json()
                return data["choices"][0]["message"]["content"], candidate
            except Exception as exc:
                last_error = f"{candidate}: {str(exc)}"
                continue

    raise Exception(
        f"All free models exhausted or rate-limited. Last error: {last_error}. "
        f"Wait a few minutes, or add credits at https://openrouter.ai/settings/credits"
    )


def extract_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```json\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip("` \n")
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _build_prompt(company_name: str, crawled_content: str, extracted_context: dict[str, Any], strict: bool = False) -> str:
    strict_suffix = (
        "Return ONLY valid JSON matching the schema exactly. Do not add commentary, markdown, or extra keys."
        if strict
        else "Return ONLY valid JSON, no markdown, no explanation."
    )
    return f"""You are a B2B research analyst scoring highly on research quality and source transparency.
Use the provided extracted evidence first. Prefer JSON-LD, regex-extracted contacts, and Serper verification snippets over guessing.
Only infer missing details when the source evidence is incomplete, and be honest in the confidence/source fields.
You have content from multiple pages of the company website such as Home, About, Products, Services, Pricing, and Contact where available.
Use ALL of them. Pricing details should come from Pricing pages when present, contact details from Contact pages, and product/service details from Products or Services pages, not just the homepage.

Produce a JSON object with EXACTLY these keys and nothing else:
{{
  "summary": "2-3 sentence company summary",
  "industry": "concise industry/category name, e.g. 'Cloud Payments' or 'Electric Vehicles'",
  "products_services": ["list", "of", "products or services"],
  "pain_points": ["3-5 likely business pain points this company faces"],
  "phone": "phone number if verified or strongly supported, else null",
  "address": "physical address if verified or strongly supported, else null",
  "competitors": ["5 real competitor company names in the same industry"],
  "confidence": {{
    "summary": "high|medium|low",
    "products_services": "high|medium|low",
    "pain_points": "high|medium|low",
    "competitors": "high|medium|low",
    "phone": "high|medium|low",
    "address": "high|medium|low"
  }},
  "sources": {{
    "summary": "short source note",
    "products_services": "short source note",
    "pain_points": "short source note",
    "competitors": "short source note",
    "phone": "short source note",
    "address": "short source note"
  }},
  "page_sources": {{
    "summary": "which page category or categories this primarily came from",
    "products_services": "which page category or categories this primarily came from",
    "pain_points": "which page category or categories this primarily came from",
    "competitors": "which page category or categories this primarily came from",
    "phone": "which page category or categories this primarily came from",
    "address": "which page category or categories this primarily came from"
  }}
}}

{strict_suffix}

COMPANY: {company_name}

EXTRACTED EVIDENCE:
{json.dumps(extracted_context, ensure_ascii=False, indent=2)[:5000]}

CRAWLED WEBSITE CONTENT:
{crawled_content[:12000]}
"""


async def analyze_company(
    company_name: str,
    crawled_content: str,
    extracted_context: dict[str, Any],
    model: str | None = None,
) -> dict[str, Any]:
    prompt = _build_prompt(company_name, crawled_content, extracted_context, strict=False)
    raw, used_model = await call_openrouter(prompt, model)

    try:
        parsed = extract_json(raw)
        validated = AnalysisResponseModel.model_validate(parsed)
        payload = validated.model_dump()
        payload["model_used"] = used_model
        return payload
    except (json.JSONDecodeError, ValidationError):
        retry_prompt = _build_prompt(company_name, crawled_content, extracted_context, strict=True)
        retry_raw, retry_model = await call_openrouter(retry_prompt, used_model)
        parsed_retry = extract_json(retry_raw)
        validated_retry = AnalysisResponseModel.model_validate(parsed_retry)
        payload = validated_retry.model_dump()
        payload["model_used"] = retry_model
        return payload

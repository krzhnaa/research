# backend/app/routes/discord.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models import ResearchResult, ApplicantInfo
from app.services.pdf_generator import generate_pdf
from app.services.discord import send_report_to_discord

router = APIRouter()


class DiscordSendPayload(BaseModel):
    bot_token: str
    channel_id: str
    applicant: ApplicantInfo
    result: ResearchResult


@router.post("/discord/send")
async def send_to_discord(payload: DiscordSendPayload):
    pdf_bytes = generate_pdf(
        payload.result.company.model_dump(),
        [c.model_dump() for c in payload.result.competitors],
        [p.model_dump() for p in payload.result.crawled_pages],
    )
    try:
        await send_report_to_discord(
            bot_token=payload.bot_token,
            channel_id=payload.channel_id,
            applicant_name=payload.applicant.name,
            applicant_email=payload.applicant.email,
            company_name=payload.result.company.company_name,
            company_website=payload.result.company.website,
            pdf_bytes=pdf_bytes,
            pdf_filename=f"{payload.result.company.company_name}_report.pdf",
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Discord send failed: {str(e)}")

    return {"status": "sent"}
# backend/app/services/discord.py
import httpx

DISCORD_API = "https://discord.com/api/v10"


async def send_report_to_discord(
    bot_token: str,
    channel_id: str,
    applicant_name: str,
    applicant_email: str,
    company_name: str,
    company_website: str,
    pdf_bytes: bytes,
    pdf_filename: str = "company_report.pdf",
):
    content = (
        f"**New Company Research Report**\n"
        f"**Applicant:** {applicant_name} ({applicant_email})\n"
        f"**Company:** {company_name}\n"
        f"**Website:** {company_website}"
    )

    async with httpx.AsyncClient(timeout=30) as client:
        files = {
            "file": (pdf_filename, pdf_bytes, "application/pdf"),
        }
        payload = {"payload_json": ('{"content": ' + repr(content).replace("'", '"') + '}')}
        # Safer: build payload_json properly
        import json
        payload = {"payload_json": json.dumps({"content": content})}

        res = await client.post(
            f"{DISCORD_API}/channels/{channel_id}/messages",
            headers={"Authorization": f"Bot {bot_token}"},
            data=payload,
            files=files,
        )
        res.raise_for_status()
        return res.json()
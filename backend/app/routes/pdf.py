# backend/app/routes/pdf.py
from fastapi import APIRouter
from fastapi.responses import Response
from app.models import ResearchResult
from app.services.pdf_generator import generate_pdf

router = APIRouter()


@router.post("/pdf")
async def generate_report_pdf(result: ResearchResult):
    pdf_bytes = generate_pdf(
        result.company.model_dump(),
        [c.model_dump() for c in result.competitors],
        [p.model_dump() for p in result.crawled_pages],
        result.crawl_metadata.model_dump() if result.crawl_metadata else None,
    )
    filename = f"{result.company.company_name.replace(' ', '_')}_report.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
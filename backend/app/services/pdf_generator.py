# backend/app/services/pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import io
import re
from datetime import datetime

NAVY = colors.HexColor("#0F172A")
ACCENT = colors.HexColor("#0EA5E9")
LIGHT_GRID = colors.HexColor("#e5e7eb")
LIGHT_BG = colors.HexColor("#f3f4f6")
ZEBRA = colors.HexColor("#f9fafb")
MUTED_TEXT = colors.HexColor("#6b7280")


def clean_text(text) -> str:
    """Replace unicode characters that break in default PDF fonts."""
    if not text:
        return ""
    text = str(text)
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00a0": " ",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    text = re.sub(r"[^\x00-\x7F]+", "", text)
    return text


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitleStyle", parent=base["Title"], fontSize=24,
                                 textColor=colors.white, spaceAfter=4, alignment=TA_LEFT),
        "subtitle": ParagraphStyle("SubtitleStyle", parent=base["Normal"], fontSize=11,
                                    textColor=colors.HexColor("#cbd5e1"), spaceAfter=2),
        "heading": ParagraphStyle("HeadingStyle", parent=base["Heading2"], fontSize=14,
                                   textColor=NAVY, spaceBefore=18, spaceAfter=8),
        "subheading": ParagraphStyle("SubHeadingStyle", parent=base["Heading3"], fontSize=11,
                                      textColor=NAVY, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("BodyStyle", parent=base["BodyText"], fontSize=10, leading=15),
        "muted": ParagraphStyle("MutedStyle", parent=base["BodyText"], fontSize=8,
                                 textColor=MUTED_TEXT, fontName="Helvetica-Oblique"),
        "bullet": ParagraphStyle("BulletStyle", parent=base["BodyText"], fontSize=10,
                                  leading=15, leftIndent=10),
    }


def _source_note(field: str, sources: dict, page_sources: dict) -> str:
    parts = []
    if sources and sources.get(field):
        parts.append(sources[field])
    if page_sources and page_sources.get(field):
        parts.append(f"page: {page_sources[field]}")
    if not parts:
        return ""
    return f" ({clean_text(', '.join(parts))})"


def _cover_and_summary(elements, styles, company, generated_at):
    header_table = Table(
        [[Paragraph("Company Research Report", styles["title"])],
         [Paragraph(clean_text(company.get("company_name", "N/A")), styles["subtitle"])],
         [Paragraph(f"Generated {generated_at}", styles["subtitle"])]],
        colWidths=[17 * cm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (0, 0), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 16))

    industry = clean_text(company.get("industry") or "")
    if industry:
        badge = Table([[Paragraph(industry.upper(), styles["muted"])]], colWidths=[6 * cm])
        badge.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("BOX", (0, 0), (-1, -1), 0.5, ACCENT),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(badge)
        elements.append(Spacer(1, 12))

    elements.append(Paragraph("Executive Summary", styles["heading"]))
    elements.append(Paragraph(clean_text(company.get("summary", "")) or "No summary available.", styles["body"]))


def _company_info_table(elements, styles, company):
    sources = company.get("sources", {}) or {}
    page_sources = company.get("page_sources", {}) or {}

    def value_with_note(field, raw_value):
        note = _source_note(field, sources, page_sources)
        val = clean_text(raw_value) or "N/A"
        if note and raw_value:
            return Paragraph(f"{val}<br/><font size=7 color='#6b7280'>{note.strip(' ()')}</font>", styles["body"])
        return Paragraph(val, styles["body"])

    elements.append(Paragraph("Company Information", styles["heading"]))
    info_data = [
        [Paragraph("<b>WEBSITE</b>", styles["muted"]), value_with_note("website", company.get("website"))],
        [Paragraph("<b>PHONE</b>", styles["muted"]), value_with_note("phone", company.get("phone"))],
        [Paragraph("<b>ADDRESS</b>", styles["muted"]), value_with_note("address", company.get("address"))],
        [Paragraph("<b>INDUSTRY</b>", styles["muted"]), value_with_note("industry", company.get("industry"))],
    ]
    table = Table(info_data, colWidths=[3.5 * cm, 13.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)


def _bulleted_section(elements, styles, title, items, note=None):
    elements.append(Paragraph(title, styles["heading"]))
    if note:
        elements.append(Paragraph(clean_text(note), styles["muted"]))
        elements.append(Spacer(1, 4))
    if not items:
        elements.append(Paragraph("No data available.", styles["body"]))
        return
    for item in items:
        elements.append(Paragraph(f"&bull;&nbsp;&nbsp;{clean_text(item)}", styles["bullet"]))


def _pages_analyzed_section(elements, styles, crawled_pages):
    elements.append(Paragraph("Pages Analyzed", styles["heading"]))
    elements.append(Paragraph(
        "The following pages were discovered and analyzed to compile this report.",
        styles["muted"],
    ))
    elements.append(Spacer(1, 6))
    if not crawled_pages:
        elements.append(Paragraph("No page-level data recorded.", styles["body"]))
        return

    rows = [[
        Paragraph("<b>CATEGORY</b>", styles["muted"]),
        Paragraph("<b>TITLE</b>", styles["muted"]),
        Paragraph("<b>URL</b>", styles["muted"]),
    ]]
    for page in crawled_pages:
        category = clean_text((page.get("category") or "other")).upper()
        title = clean_text(page.get("title") or "Untitled")
        url = clean_text(page.get("url") or "")
        rows.append([
            Paragraph(category, styles["body"]),
            Paragraph(title, styles["body"]),
            Paragraph(f"<font size=8>{url}</font>", styles["body"]),
        ])

    table = Table(rows, colWidths=[2.8 * cm, 6.2 * cm, 8 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
    ]))
    elements.append(table)


def _competitors_section(elements, styles, competitors):
    elements.append(Paragraph("Competitor Analysis", styles["heading"]))
    if not competitors:
        elements.append(Paragraph("No competitors identified.", styles["body"]))
        return
    rows = [[
        Paragraph("<b>COMPANY NAME</b>", styles["muted"]),
        Paragraph("<b>WEBSITE</b>", styles["muted"]),
    ]]
    for c in competitors:
        rows.append([
            Paragraph(clean_text(c.get("name")), styles["body"]),
            Paragraph(clean_text(c.get("website")), styles["body"]),
        ])
    table = Table(rows, colWidths=[8 * cm, 9 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, LIGHT_GRID),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
    ]))
    elements.append(table)


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED_TEXT)
    canvas.drawString(2 * cm, 1.2 * cm, "Generated by Company Research AI")
    canvas.drawRightString(19 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def generate_pdf(company: dict, competitors: list, crawled_pages: list | None = None) -> bytes:
    """
    Generates a page-wise, topic-organized PDF report.
    company: dict matching CompanyInfo fields (may include sources/page_sources)
    competitors: list of {"name":..., "website":...}
    crawled_pages: optional list of {"url","title","category"} to show crawl coverage
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm,
    )
    styles = _styles()
    elements = []

    generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")

    _cover_and_summary(elements, styles, company, generated_at)
    elements.append(Spacer(1, 10))
    _company_info_table(elements, styles, company)

    sources = company.get("sources", {}) or {}
    page_sources = company.get("page_sources", {}) or {}

    _bulleted_section(
        elements, styles, "Products & Services",
        company.get("products_services", []),
        note=("Compiled from: " + page_sources["products_services"])
        if page_sources.get("products_services") else None,
    )

    elements.append(Spacer(1, 6))
    _bulleted_section(
        elements, styles, "AI-Generated Pain Points",
        company.get("pain_points", []),
        note="AI-inferred based on company positioning, products, and market context.",
    )

    if crawled_pages:
        elements.append(PageBreak())
        _pages_analyzed_section(elements, styles, crawled_pages)

    elements.append(PageBreak())
    _competitors_section(elements, styles, competitors)

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer.read()
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle


def generate_pdf_report(r: dict) -> bytes:
    """
    Generates a professional PDF report from the analysis result dict.
    Returns raw bytes — Streamlit serves these as a file download.

    Uses ReportLab's platypus layout engine which works like building blocks:
    - Paragraph: a block of text with a style
    - Table: rows and columns (used for cards and side-by-side layout)
    - Spacer: empty vertical space
    - HRFlowable: a horizontal rule (divider line)
    - KeepTogether: keeps a group of elements on the same page
    """
    buffer = io.BytesIO()
    doc    = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=18*mm,  bottomMargin=18*mm,
    )

    # ── Colours ────────────────────────────────────────────────────────────────
    INK        = colors.HexColor("#111118")
    SUBTEXT    = colors.HexColor("#555566")
    LIME_DARK  = colors.HexColor("#4A7C00")
    LIME_BG    = colors.HexColor("#F2FAD8")
    BLUE_DARK  = colors.HexColor("#2D3A8C")
    BLUE_BG    = colors.HexColor("#EEF0FA")
    AMBER_DARK = colors.HexColor("#7A4A00")
    AMBER_BG   = colors.HexColor("#FDF3E3")
    RULE       = colors.HexColor("#DDDDEE")
    HEADER_BG  = colors.HexColor("#111118")
    page_w     = A4[0] - 40*mm

    # ── Text styles ────────────────────────────────────────────────────────────
    logo_s        = ParagraphStyle("logo",     fontName="Helvetica-Bold", fontSize=17, textColor=colors.white)
    badge_s       = ParagraphStyle("badge",    fontName="Helvetica", fontSize=7, textColor=colors.HexColor("#AAAACC"), alignment=2, leading=10)
    eyebrow_s     = ParagraphStyle("eyebrow",  fontName="Helvetica", fontSize=7.5, textColor=LIME_DARK, spaceAfter=5, letterSpacing=1.5)
    title_s       = ParagraphStyle("title",    fontName="Helvetica-Bold", fontSize=22, textColor=INK, spaceAfter=5, leading=28)
    meta_s        = ParagraphStyle("meta",     fontName="Helvetica", fontSize=8, textColor=SUBTEXT, spaceAfter=0)
    card_lbl_lime = ParagraphStyle("cl_lime",  fontName="Helvetica-Bold", fontSize=7.5, textColor=LIME_DARK,  spaceAfter=7, letterSpacing=1.5)
    card_lbl_blue = ParagraphStyle("cl_blue",  fontName="Helvetica-Bold", fontSize=7.5, textColor=BLUE_DARK,  spaceAfter=7, letterSpacing=1.5)
    card_lbl_amb  = ParagraphStyle("cl_amber", fontName="Helvetica-Bold", fontSize=7.5, textColor=AMBER_DARK, spaceAfter=7, letterSpacing=1.5)
    body_s        = ParagraphStyle("body",     fontName="Helvetica", fontSize=10, textColor=INK, leading=16, spaceAfter=0)
    bullet_s      = ParagraphStyle("bullet",   fontName="Helvetica", fontSize=10, textColor=INK, leading=15, spaceAfter=4, leftIndent=10)
    footer_s      = ParagraphStyle("footer",   fontName="Helvetica", fontSize=7, textColor=SUBTEXT, alignment=1)

    story = []

    # ── Header bar ─────────────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph("DocLens", logo_s),
        Paragraph("AI DOCUMENT INTELLIGENCE<br/>Smart Summarization Report", badge_s),
    ]], colWidths=[page_w*0.55, page_w*0.45])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), HEADER_BG),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("LEFTPADDING",   (0,0),(0,-1),  14),
        ("RIGHTPADDING",  (-1,0),(-1,-1),14),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story += [
        hdr,
        Spacer(1, 8*mm),
        Paragraph("ANALYSIS REPORT  -  SMART SUMMARIZATION", eyebrow_s),
        Paragraph(f"Summary of {r['file_name']}", title_s),
        Paragraph(f"Domain: {r['category']}    Style: {r['detail_level']}", meta_s),
        Spacer(1, 4*mm),
        HRFlowable(width="100%", thickness=0.75, color=RULE, spaceAfter=6*mm),
    ]

    # ── Executive Summary card ─────────────────────────────────────────────────
    card_style = lambda bg, line: TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("LINEBELOW",     (0,0),(-1,-1), 2, line),
    ])

    story.append(KeepTogether([
        Paragraph("EXECUTIVE SUMMARY", card_lbl_lime),
        Table([[Paragraph(r["executive_summary"], body_s)]], colWidths=[page_w], style=card_style(LIME_BG, LIME_DARK)),
        Spacer(1, 5*mm),
    ]))

    # ── Key Points card ────────────────────────────────────────────────────────
    kp_paras = [Paragraph(f"- {pt}", bullet_s) for pt in r["key_points"]]
    story.append(KeepTogether([
        Paragraph("KEY POINTS", card_lbl_lime),
        Table([[kp_paras]], colWidths=[page_w], style=card_style(LIME_BG, LIME_DARK)),
        Spacer(1, 5*mm),
    ]))

    # ── Action Items + Data Highlights side by side ────────────────────────────
    col_w  = (page_w - 5*mm) / 2
    ai_col = [Paragraph("ACTION ITEMS",   card_lbl_blue)] + [Paragraph(f"- {a}", bullet_s) for a in r["action_items"]]
    dh_col = [Paragraph("DATA HIGHLIGHTS", card_lbl_amb)] + [Paragraph(f"- {d}", bullet_s) for d in r["data_highlights"]]

    side = Table([[ai_col, dh_col]], colWidths=[col_w, col_w])
    side.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(0,-1), BLUE_BG),
        ("BACKGROUND",    (1,0),(1,-1), AMBER_BG),
        ("LEFTPADDING",   (0,0),(-1,-1), 14),
        ("RIGHTPADDING",  (0,0),(-1,-1), 14),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("LINEBELOW",     (0,0),(0,-1), 2, BLUE_DARK),
        ("LINEBELOW",     (1,0),(1,-1), 2, AMBER_DARK),
    ]))
    story += [
        side,
        Spacer(1, 10*mm),
        HRFlowable(width="100%", thickness=0.5, color=RULE, spaceAfter=3*mm),
        Paragraph("Generated by DocLens  -  AI Document Intelligence", footer_s),
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

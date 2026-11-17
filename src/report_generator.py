
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether
)


# --------------------------------------------------
# COLORS
# --------------------------------------------------

NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#2874A6")
LIGHT_BLUE = colors.HexColor("#EAF2F8")

GREEN = colors.HexColor("#D5F5E3")
DARK_GREEN = colors.HexColor("#196F3D")

RED = colors.HexColor("#FADBD8")
DARK_RED = colors.HexColor("#922B21")

LIGHT_GREY = colors.HexColor("#F4F6F7")
DARK_GREY = colors.HexColor("#566573")


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def safe_paragraph(value, style):
    """Safely convert dynamic text into a PDF paragraph."""

    return Paragraph(
        escape(str(value)).replace("\n", "<br/>"),
        style
    )


def draw_page(canvas, document):
    """Add a consistent header and footer to every page."""

    canvas.saveState()

    width, height = A4

    # Header line
    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(1.5)

    canvas.line(
        18 * mm,
        height - 14 * mm,
        width - 18 * mm,
        height - 14 * mm
    )

    # Footer line
    canvas.setStrokeColor(colors.lightgrey)

    canvas.line(
        18 * mm,
        14 * mm,
        width - 18 * mm,
        14 * mm
    )

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GREY)

    canvas.drawString(
        18 * mm,
        9 * mm,
        "BusinessDoc AI | Human review required"
    )

    canvas.drawRightString(
        width - 18 * mm,
        9 * mm,
        f"Page {document.page}"
    )

    canvas.restoreState()


def clean_ai_explanation(explanation):
    """Convert basic Markdown formatting into readable PDF text."""

    lines = []

    for line in str(explanation).splitlines():

        line = line.strip()

        if not line:
            lines.append("")
            continue

        # Convert Markdown headings into plain text.
        while line.startswith("#"):
            line = line[1:].strip()

        # Convert Markdown bullets.
        if line.startswith("- ") or line.startswith("* "):
            line = "• " + line[2:]

        # Remove simple bold and italic markers.
        line = line.replace("**", "")
        line = line.replace("__", "")
        line = line.replace("*", "")
        line = line.replace("_", "")

        lines.append(escape(line))

    return "<br/>".join(lines)


# --------------------------------------------------
# MAIN REPORT GENERATOR
# --------------------------------------------------

def generate_report(results, explanation=None):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=23 * mm,
        bottomMargin=21 * mm,
        title="BusinessDoc AI Reconciliation Report",
        author="BusinessDoc AI"
    )

    styles = getSampleStyleSheet()

    # --------------------------------------------------
    # CUSTOM STYLES
    # --------------------------------------------------

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=DARK_GREY,
        spaceAfter=12
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#283747")
    )

    table_header_style = ParagraphStyle(
        "TableHeader",
        parent=normal_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        fontSize=7
    )

    table_cell_style = ParagraphStyle(
        "TableCell",
        parent=normal_style,
        fontSize=7,
        leading=9,
        wordWrap="CJK"
    )

    status_style = ParagraphStyle(
        "Status",
        parent=normal_style,
        fontName="Helvetica-Bold",
        fontSize=7,
        alignment=TA_CENTER
    )

    story = []

    # --------------------------------------------------
    # REPORT HEADER
    # --------------------------------------------------

    story.append(
        Paragraph("BusinessDoc AI", title_style)
    )

    story.append(
        Paragraph(
            "INVOICE &amp; PURCHASE ORDER RECONCILIATION",
            subtitle_style
        )
    )

    report_date = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    story.append(
        Paragraph(
            f"<b>Generated on:</b> {escape(report_date)}",
            normal_style
        )
    )

    story.append(Spacer(1, 12))

    # --------------------------------------------------
    # CALCULATE SUMMARY
    # --------------------------------------------------

    total_checks = len(results)

    matches = sum(
        1 for item in results
        if item["status"] == "MATCH"
    )

    mismatches = [
        item for item in results
        if item["status"] == "MISMATCH"
    ]

    # --------------------------------------------------
    # SUMMARY SECTION
    # --------------------------------------------------

    story.append(
        Paragraph("Reconciliation Summary", section_style)
    )

    summary_data = [
        ["TOTAL CHECKS", "MATCHES", "DISCREPANCIES"],
        [
            str(total_checks),
            str(matches),
            str(len(mismatches))
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[55 * mm, 55 * mm, 55 * mm],
        rowHeights=[10 * mm, 15 * mm]
    )

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
            ("TEXTCOLOR", (0, 1), (-1, 1), NAVY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, 1), 18),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.white),
            ("PADDING", (0, 0), (-1, -1), 6)
        ])
    )

    story.append(summary_table)
    story.append(Spacer(1, 14))

    # --------------------------------------------------
    # OVERALL STATUS
    # --------------------------------------------------

    if mismatches:

        status_text = (
            f"<b>{len(mismatches)} discrepancy(s) detected.</b> "
            "Human review is required before proceeding."
        )

        status_background = RED
        status_color = DARK_RED

    else:

        status_text = (
            "<b>All checked fields match.</b> "
            "No discrepancies were detected."
        )

        status_background = GREEN
        status_color = DARK_GREEN

    overall_status = Table(
        [[Paragraph(status_text, normal_style)]],
        colWidths=[165 * mm]
    )

    overall_status.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), status_background),
            ("TEXTCOLOR", (0, 0), (-1, -1), status_color),
            ("BOX", (0, 0), (-1, -1), 0.5, status_color),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 9)
        ])
    )

    story.append(overall_status)
    story.append(Spacer(1, 14))

    # --------------------------------------------------
    # DETAILED COMPARISON
    # --------------------------------------------------

    story.append(
        Paragraph("Detailed Comparison", section_style)
    )

    table_data = [[
        Paragraph("FIELD", table_header_style),
        Paragraph("PURCHASE ORDER", table_header_style),
        Paragraph("INVOICE", table_header_style),
        Paragraph("STATUS", table_header_style)
    ]]

    mismatch_rows = []

    for index, item in enumerate(results, start=1):

        status = item["status"]

        table_data.append([
            safe_paragraph(item["field"], table_cell_style),
            safe_paragraph(item["purchase_order"], table_cell_style),
            safe_paragraph(item["invoice"], table_cell_style),
            Paragraph(status, status_style)
        ])

        if status == "MISMATCH":
            mismatch_rows.append(index)

    comparison_table = Table(
        table_data,
        colWidths=[40 * mm, 48 * mm, 48 * mm, 29 * mm],
        repeatRows=1,
        hAlign="LEFT"
    )

    table_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5D8DC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
    ]

    # Alternate row backgrounds.
    for row in range(1, len(table_data)):

        if row % 2 == 0:
            table_commands.append(
                ("BACKGROUND", (0, row), (-1, row), LIGHT_GREY)
            )

    # Highlight mismatches.
    for row in mismatch_rows:

        table_commands.extend([
            ("BACKGROUND", (3, row), (3, row), RED),
            ("TEXTCOLOR", (3, row), (3, row), DARK_RED)
        ])

    # Highlight matching statuses.
    for row in range(1, len(table_data)):

        if row not in mismatch_rows:
            table_commands.extend([
                ("BACKGROUND", (3, row), (3, row), GREEN),
                ("TEXTCOLOR", (3, row), (3, row), DARK_GREEN)
            ])

    comparison_table.setStyle(
        TableStyle(table_commands)
    )

    story.append(comparison_table)

    # --------------------------------------------------
    # DISCREPANCIES
    # --------------------------------------------------

    if mismatches:

        story.append(
            Paragraph(
                "Issues Requiring Attention",
                section_style
            )
        )

        for item in mismatches:

            issue_content = [
                Paragraph(
                    f"<b>{escape(str(item['field']))}</b>",
                    normal_style
                ),
                Spacer(1, 4),
                Paragraph(
                    f"<b>Purchase Order:</b> "
                    f"{escape(str(item['purchase_order']))}",
                    normal_style
                ),
                Paragraph(
                    f"<b>Invoice:</b> "
                    f"{escape(str(item['invoice']))}",
                    normal_style
                )
            ]

            issue_box = Table(
                [[issue_content]],
                colWidths=[165 * mm]
            )

            issue_box.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), RED),
                    ("BOX", (0, 0), (-1, -1), 0.5, DARK_RED),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8)
                ])
            )

            story.append(
                KeepTogether([
                    issue_box,
                    Spacer(1, 8)
                ])
            )

    # --------------------------------------------------
    # AI EXPLANATION
    # --------------------------------------------------

    if explanation:

        story.append(
            Paragraph(
                "AI-Powered Explanation",
                section_style
            )
        )

        safe_explanation = clean_ai_explanation(
            explanation
        )

        story.append(
            Paragraph(
                safe_explanation,
                normal_style
            )
        )

    # --------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "<b>Important:</b> This report is generated "
            "automatically. Detected discrepancies require "
            "human review. This report does not authorize "
            "payment approval or rejection.",
            styles["Italic"]
        )
    )

    # --------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------

    document.build(
        story,
        onFirstPage=draw_page,
        onLaterPages=draw_page
    )

    buffer.seek(0)

    return buffer.getvalue()

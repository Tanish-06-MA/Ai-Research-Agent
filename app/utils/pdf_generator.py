from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import os
import re


def _sanitize_text(text):
    """
    Sanitize text for ReportLab XML parser.
    Replaces characters that break Paragraph rendering.
    """
    # Escape XML special characters
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    # Remove or replace other problematic characters
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def generate_pdf(report, query):
    """
    Generate a PDF report from the research output.

    Creates a uniquely-named PDF in the outputs/ directory using a timestamp.
    Handles special characters that can break ReportLab's XML parser.

    Args:
        report: The research report text (markdown-formatted).
        query:  The user's original query (used as subtitle).

    Returns:
        Path to the generated PDF file.
    """
    os.makedirs("outputs", exist_ok=True)

    # Unique filename using timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = re.sub(r"[^\w\s-]", "", query)[:50].strip().replace(" ", "_")
    pdf_path = f"outputs/report_{safe_query}_{timestamp}.pdf"

    try:
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]
        body_style = styles["BodyText"]

        story = []

        story.append(Paragraph("AI Research Report", title_style))
        story.append(Spacer(1, 20))
        story.append(
            Paragraph(f"<b>Query:</b> {_sanitize_text(query)}", body_style)
        )
        story.append(Spacer(1, 20))

        for line in report.split("\n"):
            line = line.strip()

            if not line:
                story.append(Spacer(1, 8))
                continue

            sanitized = _sanitize_text(line)

            if line.startswith("## "):
                heading = sanitized.replace("## ", "", 1)
                story.append(Paragraph(heading, heading_style))

            elif line.startswith("# "):
                heading = sanitized.replace("# ", "", 1)
                story.append(Paragraph(heading, title_style))

            elif line.startswith("- "):
                text = sanitized.replace("- ", "• ", 1)
                story.append(Paragraph(text, body_style))

            else:
                story.append(Paragraph(sanitized, body_style))

        doc.build(story)

        return pdf_path

    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        # Fallback: save as plain text
        txt_path = pdf_path.replace(".pdf", ".txt")
        try:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"Query: {query}\n\n{report}")
            print(f"Saved report as plain text: {txt_path}")
            return txt_path
        except Exception:
            return ""

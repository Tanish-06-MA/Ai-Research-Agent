from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import os


def generate_pdf(report, query):
    os.makedirs("outputs", exist_ok=True)

    pdf_path = "outputs/research_report.pdf"

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

    story.append(Paragraph(f"<b>Query:</b> {query}", body_style))

    story.append(Spacer(1, 20))

    for line in report.split("\n"):
        line = line.strip()

        if not line:
            story.append(Spacer(1, 8))
            continue

        if line.startswith("## "):
            heading = line.replace("## ", "", 1)
            story.append(Paragraph(heading, heading_style))

        elif line.startswith("# "):
            heading = line.replace("# ", "", 1)
            story.append(Paragraph(heading, title_style))

        elif line.startswith("- "):
            text = line.replace("- ", "• ", 1)
            story.append(Paragraph(text, body_style))

        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)

    return pdf_path

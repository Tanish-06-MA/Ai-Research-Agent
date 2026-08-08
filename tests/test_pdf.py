from app.tools.pdf_loader import load_pdf

pdf_path = "tests/Research_Paper.pdf"

text = load_pdf(pdf_path)

print(text[:3000])

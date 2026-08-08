from app.tools.text_chunker import chunk_text
from app.tools.pdf_loader import load_pdf


pdf_path = "tests/Research_Paper.pdf"

text = load_pdf(pdf_path)

chunks = chunk_text(text)

print("\nTotal chunks:", len(chunks))

for i, chunk in enumerate(chunks):
    print(f"\n--- Chunk {i + 1} ---")
    print(chunk[:500])

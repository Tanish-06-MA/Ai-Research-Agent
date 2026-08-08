from app.tools.pdf_loader import load_pdf
from app.tools.text_chunker import chunk_text
from app.tools.embeddings import generate_embeddings


pdf_path = "tests/Research_Paper.pdf"

text = load_pdf(pdf_path)

chunks = chunk_text(text)

embeddings = generate_embeddings(chunks)

print("Total chunks:", len(chunks))
print("Total embeddings:", len(embeddings))

print("First embedding:")
print(embeddings[0])

print("Embedding dimensions:")
print(len(embeddings[0]))

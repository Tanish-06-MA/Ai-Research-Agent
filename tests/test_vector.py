from app.tools.pdf_loader import load_pdf
from app.tools.text_chunker import chunk_text
from app.tools.embeddings import generate_embeddings
from app.tools.vector_store import store_chunks


pdf_path = "tests/Research_Paper.pdf"

text = load_pdf(pdf_path)

chunks = chunk_text(text)

embeddings = generate_embeddings(chunks)

store_chunks(chunks, embeddings)

print("Chunks stored successfully!")
print("Total chunks:", len(chunks))

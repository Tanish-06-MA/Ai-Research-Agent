import sys

try:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(f"[ERROR] Failed to load embedding model 'all-MiniLM-L6-v2': {e}")
    print("Please check your internet connection or install the model manually.")
    model = None


def generate_embeddings(chunks: list[str]):
    """Generate embeddings for a list of text chunks."""
    if model is None:
        print("[ERROR] Embedding model is not available. Cannot generate embeddings.")
        return []

    embeddings = model.encode(chunks)
    return embeddings

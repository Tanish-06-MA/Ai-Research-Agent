import chromadb
from app.tools.embeddings import generate_embeddings

client = chromadb.PersistentClient(path="./chroma_db")

PDF_DISTANCE_THRESHOLD = 1.40


def _get_collection():
    """Safely get the ChromaDB collection. Returns None if it doesn't exist."""
    try:
        return client.get_collection(name="research_document")
    except Exception:
        return None


def has_pdf_collection() -> bool:
    """Check whether a PDF collection exists and has documents."""
    collection = _get_collection()
    if collection is None:
        return False
    try:
        return collection.count() > 0
    except Exception:
        return False


def retrieve_query(query, top_k=3, threshold=PDF_DISTANCE_THRESHOLD):
    """
    Retrieve the most relevant PDF chunks for a query using semantic search.

    Returns a list of dicts with 'content', 'source', and 'distance' keys.
    Returns an empty list if no collection exists, embeddings fail, or no
    chunks pass the distance threshold.
    """
    collection = _get_collection()
    if collection is None:
        print("PDF RETRIEVAL: No PDF collection found.")
        return []

    embeddings = generate_embeddings([query])
    if not len(embeddings):
        print("PDF RETRIEVAL: Embedding generation failed.")
        return []

    query_embedding = embeddings[0]

    try:
        results = collection.query(
            query_embeddings=[query_embedding.tolist()
                              if hasattr(query_embedding, "tolist")
                              else query_embedding],
            n_results=top_k,
        )
    except Exception as e:
        print(f"PDF RETRIEVAL: ChromaDB query failed: {e}")
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print(f"PDF distances: {distances}")

    retrieved_documents = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        if distance <= threshold:
            retrieved_documents.append(
                {
                    "content": document,
                    "source": metadata.get("source", "Unknown PDF"),
                    "distance": distance,
                }
            )

    print(f"Relevant PDF chunks: {len(retrieved_documents)}")
    return retrieved_documents

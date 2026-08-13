# import chromadb
# from chromadb import PersistentClient
# from app.tools.embeddings import generate_embeddings


# client = chromadb.PersistentClient(path="./chroma_db")

# # Retrieving the collection made during chunk storage
# collection = client.get_collection(name="research_document")


# def retrieve_query(query, top_k=3):  # top_k=> Means TOP 3 RELEVANT CHUNKS
#     query_embeddings = generate_embeddings([query])[0]

#     results = collection.query(query_embeddings=[query_embeddings], n_results=top_k)

#     documents = results["documents"][0]
#     metadatas = results["metadatas"][0]

#     retrieved_documents = []

#     for document, metadata in zip(documents, metadatas):
#         retrieved_documents.append(
#             {"content": document, "source": metadata.get("source", "Unknown PDF")}
#         )

#     return retrieved_documents


# New Code
import chromadb
from app.tools.embeddings import generate_embeddings

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_collection(name="research_document")


PDF_DISTANCE_THRESHOLD = 1.20


def retrieve_query(query, top_k=3, threshold=1.4):

    query_embeddings = generate_embeddings([query])[0]

    results = collection.query(query_embeddings=[query_embeddings], n_results=top_k)

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

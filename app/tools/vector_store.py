import chromadb
from chromadb import PersistentClient

client = PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="research_document")


def store_chunks(chunks, embeddings):
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(ids=ids, documents=chunks, embeddings=embeddings.tolist())

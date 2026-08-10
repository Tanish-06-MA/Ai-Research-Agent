from app.tools.retriever import retrieve_query


query = "What is LangGraph?"

results = retrieve_query(query)

print("\nRetrieved Chunks:\n")

for i, chunk in enumerate(results, 1):
    print(f"\n--- Chunk {i} ---")
    print(chunk)

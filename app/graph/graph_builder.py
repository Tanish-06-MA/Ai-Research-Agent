from langgraph.graph import StateGraph, START, END
from app.graph.states import ResearchState
from app.graph.nodes import (
    intent_node,
    retrieve_node,
    plan_node,
    search_node,
    summarize_node,
)


def route_by_intent(state: ResearchState) -> str:
    """
    Route the graph based on detected intent.

    Returns the name of the next node to execute:
      - PDF_ONLY    → retrieve (then summarize)
      - WEB_ONLY    → plan (then search, then summarize)
      - PDF_AND_WEB → retrieve_and_search (then summarize)
    """
    intent = state.get("intent", "WEB_ONLY")

    if intent == "PDF_ONLY":
        return "retrieve"
    elif intent == "PDF_AND_WEB":
        return "retrieve_and_search"
    else:
        return "plan"


def retrieve_and_search_node(state: ResearchState):
    """
    Combined node for PDF_AND_WEB: retrieves PDF chunks and executes web search
    using the search plan already generated during intent_node.
    """
    from app.tools.retriever import retrieve_query
    from app.tools.search import web_search

    query = state["query"]

    # --- Retrieve PDF chunks (reuse probe if available) ---
    existing_docs = state.get("documents", [])
    if existing_docs:
        documents = existing_docs
        pdf_relevant = True
        print(f"PDF RETRIEVAL: Reusing {len(documents)} pre-retrieved chunks")
    else:
        documents = retrieve_query(query, top_k=3)
        pdf_relevant = bool(documents)
    print(f"PDF RETRIEVAL: {'Found' if pdf_relevant else 'No relevant'} chunks ({len(documents)})")

    # --- Read pre-generated plan from state ---
    plan = state.get("plan", "").strip()
    if not plan:
        plan = f"1. {query}"

    tasks = []
    for line in plan.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit():
            task = line.split(".", 1)[1].strip() if "." in line else line
            tasks.append(task)

    if not tasks:
        tasks = [query]

    all_results = []
    all_sources = []
    seen_urls = set()

    for task in tasks:
        results = web_search(task)
        all_results.append({"task": task, "results": results})
        for result in results:
            url = result.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(url)

    print(f"SOURCE ROUTING: PDF_AND_WEB")
    print(f"WEB SEARCH: {len(all_sources)} unique sources found")

    return {
        "documents": documents,
        "pdf_relevant": pdf_relevant,
        "plan": plan,
        "search_results": all_results,
        "sources": all_sources,
    }


# --- Build the graph ---

graph = StateGraph(ResearchState)

# Register nodes
graph.add_node("intent", intent_node)
graph.add_node("retrieve", retrieve_node)
graph.add_node("plan", plan_node)
graph.add_node("search", search_node)
graph.add_node("retrieve_and_search", retrieve_and_search_node)
graph.add_node("summarize", summarize_node)

# Edges
graph.add_edge(START, "intent")

# Conditional routing from intent node
graph.add_conditional_edges(
    "intent",
    route_by_intent,
    {
        "retrieve": "retrieve",             # PDF_ONLY path
        "plan": "plan",                     # WEB_ONLY path
        "retrieve_and_search": "retrieve_and_search",  # PDF_AND_WEB path
    },
)

# PDF_ONLY: retrieve → summarize
graph.add_edge("retrieve", "summarize")

# WEB_ONLY: plan → search → summarize
graph.add_edge("plan", "search")
graph.add_edge("search", "summarize")

# PDF_AND_WEB: retrieve_and_search → summarize
graph.add_edge("retrieve_and_search", "summarize")

# All paths end at summarize
graph.add_edge("summarize", END)

app = graph.compile()

from app.tools.search import web_search
from app.graph.states import ResearchState
from app.llm.groq_client import generate_summary
from app.tools.retriever import retrieve_query, has_pdf_collection
from app.planner.intent import detect_intent


def intent_node(state: ResearchState):
    """
    First node in the graph. Detects the source intent and creates the search plan
    in a single LLM API call (saving 1 API call per web search).

    Checks if a PDF collection exists, probes for relevant chunks to
    provide context to the intent detector, then routes accordingly.

    Also stores the probe results in state so retrieve_node can reuse them
    instead of re-querying with a vague follow-up query like "explain this simply".
    """
    query = state["query"]
    conversation_history = state.get("conversation_history", "")

    # Check if PDF data is available
    has_pdf = has_pdf_collection()

    # Probe for relevant PDF chunks to give the intent detector context
    relevant_chunks = 0
    probe_documents = []
    if has_pdf:
        probe_documents = retrieve_query(query, top_k=3)
        relevant_chunks = len(probe_documents)

    intent, plan = detect_intent(
        query=query,
        conversation_history=conversation_history,
        has_pdf=has_pdf,
        relevant_pdf_chunks=relevant_chunks,
    )

    print(f"SOURCE INTENT: {intent}")
    print(f"PDF available: {has_pdf}")
    if has_pdf:
        print(f"Relevant PDF chunks (probe): {relevant_chunks}")

    # Store routing, plan, and probe results so downstream nodes can reuse them.
    return {
        "intent": intent,
        "plan": plan,
        "documents": probe_documents,
        "pdf_relevant": bool(probe_documents),
    }


def retrieve_node(state: ResearchState):
    """
    Retrieve relevant PDF chunks for the query.

    Only runs when the graph routes here (PDF_ONLY).
    If intent_node already found relevant documents during its probe,
    reuses those instead of re-querying (important for follow-up queries).
    """
    existing_docs = state.get("documents", [])
    if existing_docs:
        print(f"PDF RETRIEVAL: Reusing {len(existing_docs)} pre-retrieved chunks")
        return {
            "documents": existing_docs,
            "pdf_relevant": True,
        }

    # Otherwise retrieve fresh
    query = state["query"]
    documents = retrieve_query(query, top_k=3)
    pdf_relevant = bool(documents)

    print(f"PDF RETRIEVAL: {'Found' if pdf_relevant else 'No relevant'} chunks ({len(documents)})")

    return {
        "documents": documents,
        "pdf_relevant": pdf_relevant,
    }


def plan_node(state: ResearchState):
    """
    Returns the search plan generated during the intent node.
    Does NOT call the LLM again, saving one API call.
    """
    plan = state.get("plan", "").strip()
    if not plan:
        plan = f"1. {state['query']}"  # Fallback

    print(f"SOURCE ROUTING: {state.get('intent', 'UNKNOWN')}")
    return {"plan": plan}


def search_node(state: ResearchState):
    """
    Execute web searches based on the research plan.

    Only runs when the graph routes here (WEB_ONLY).
    """
    plan = state.get("plan", "")

    tasks = []
    for line in plan.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit():
            task = line.split(".", 1)[1].strip() if "." in line else line
            tasks.append(task)

    # Fallback: if no tasks were parsed, use the query
    if not tasks:
        tasks = [state["query"]]

    all_results = []
    all_sources = []
    seen_urls = set()

    for task in tasks:
        results = web_search(task)

        all_results.append(
            {
                "task": task,
                "results": results,
            }
        )

        for result in results:
            url = result.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_sources.append(url)

    print(f"WEB SEARCH: {len(all_sources)} unique sources found")

    return {
        "search_results": all_results,
        "sources": all_sources,
    }


def summarize_node(state: ResearchState):
    """
    Generate the final research report and update conversation history.

    Receives all gathered data (PDF chunks, web results, or both) and
    produces the report. Conversation history is updated here — the only
    place it should be updated to avoid duplication.
    """
    intent = state.get("intent", "")
    conversation_history = state.get("conversation_history", "")

    summary = generate_summary(
        query=state["query"],
        plan=state.get("plan", ""),
        search_results=state.get("search_results", []),
        documents=state.get("documents", []),
        conversation_history=conversation_history,
        intent=intent,
    )

    # Update conversation history (single point of update — no duplication)
    updated_history = conversation_history
    updated_history += f"\nUser: {state['query']}\nAssistant: {summary}\n"

    return {
        "draft_summary": summary,
        "conversation_history": updated_history,
    }

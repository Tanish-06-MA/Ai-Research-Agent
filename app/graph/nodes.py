from app.tools.search import web_search
from app.graph.states import ResearchState
from app.planner.planner import create_plan
from app.llm.groq_client import generate_summary
from app.tools.retriever import retrieve_query
from app.planner.intent import detect_intent


def plan_node(state: ResearchState):

    has_pdf = len(state["documents"]) > 0

    intent = detect_intent(
        query=state["query"],
        conversation_history=state["conversation_history"],
        has_pdf=has_pdf,
        relevant_pdf_chunks=state.get("relevant_pdf_chunks", 0),
    )

    state["intent"] = intent

    print(f"SOURCE INTENT: {intent}")
    print(f"Relevant PDF chunks: {len(state['documents'])}")

    if intent == "PDF_ONLY":
        state["plan"] = ""
        return state

    plan = create_plan(state["query"])
    state["plan"] = plan

    return state


def search_node(state: ResearchState):
    intent = state["intent"]

    # PDF only → web search mat karo
    if intent == "PDF_ONLY":
        state["search_results"] = []
        state["sources"] = []

        print("SOURCE ROUTING: PDF ONLY")
        return state

    plan = state["plan"]

    tasks = []
    for line in plan.split("\n"):
        line = line.strip()

        if not line:
            continue

        if line[0].isdigit():
            task = line.split(".", 1)[1].strip()
            tasks.append(task)

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

    state["search_results"] = all_results
    state["sources"] = all_sources

    print(f"SOURCE ROUTING: {intent}")

    return state


def retrieve_node(state: ResearchState):
    query = state["query"]
    intent = state["intent"]

    # WEB_ONLY → PDF retrieval ki zarurat nahi
    if intent == "WEB_ONLY":
        state["documents"] = []
        state["pdf_relevant"] = False

        print("PDF RETRIEVAL: SKIPPED")
        return state

    documents = retrieve_query(query, top_k=3)

    state["documents"] = documents
    state["pdf_relevant"] = bool(documents)

    print(f"Relevant PDF chunks: {len(documents)}")

    return state


def summarize_node(state: ResearchState):
    summary = generate_summary(
        state["query"],
        state["plan"],
        state["search_results"],
        state["documents"],
        state["conversation_history"],
    )

    state["draft_summary"] = summary

    # Current conversation ko history me add karo
    state["conversation_history"] += f"\nUser: {state['query']}\nAssistant: {summary}\n"

    return state

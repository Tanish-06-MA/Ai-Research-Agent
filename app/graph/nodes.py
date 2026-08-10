from app.tools.search import web_search
from app.graph.states import ResearchState
from app.planner.planner import create_plan
from app.llm.groq_client import generate_summary
from app.tools.retriever import retrieve_query


def plan_node(state: ResearchState):

    plan = create_plan(state["query"])
    state["plan"] = plan
    return state


def search_node(state: ResearchState):
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
    return state


def retrieve_node(state: ResearchState):
    """
    Retrieves the embeddings
    """
    query = state["query"]

    documents = retrieve_query(query, top_k=3)

    return {"documents": documents}


def summarize_node(state: ResearchState):
    summary = generate_summary(
        state["query"], state["plan"], state["search_results"], state["documents"]
    )
    state["draft_summary"] = summary
    return state

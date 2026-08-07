from app.tools.search import web_search
from app.graph.states import ResearchState
from app.planner.planner import create_plan
from app.llm.groq_client import generate_summary


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
            taks = line.split(".", 1)[1].strip()
            tasks.append(taks)

    all_results = []
    all_sources = []

    for task in tasks:
        results = web_search(task)

        all_results.append(results)

        for r in results:
            all_sources.append(r["url"])

    state["search_results"] = all_results
    state["sources"] = all_sources
    return state


def summarize_node(state: ResearchState):
    summary = generate_summary(state["query"], state["search_results"])

    state["draft_summary"] = summary
    return state

from app.graph.states import ResearchState
from app.planner.planner import create_plan


def plan_node(state: ResearchState):

    plan = create_plan(state["query"])
    state["plan"] = plan
    return state


def search_node(state: ResearchState):
    return state


def summarize_node(state: ResearchState):
    return state

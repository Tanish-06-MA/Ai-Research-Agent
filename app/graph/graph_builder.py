from app.graph.nodes import summarize_node
from app.graph.nodes import search_node
from app.graph.nodes import plan_node
from langgraph.graph import StateGraph, START, END
from app.graph.states import ResearchState

graph = StateGraph(ResearchState)

graph.add_node("plan", plan_node)
# graph.add_node("search", search_node)
# graph.add_node("summarize", summarize_node)

graph.add_edge(START, "plan")
# graph.add_edge("plan", "search")
# graph.add_edge("search", "summarize")
# graph.add_edge("summarize", END)
graph.add_edge("plan", END)

app = graph.compile()

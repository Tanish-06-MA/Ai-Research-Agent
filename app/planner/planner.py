import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(override=True)

api = os.environ.get("GEMINI_API_KEY")

model = ChatOpenAI(
    model="gemini-3.5-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=api,
)


def detect_comparison(query: str) -> bool:
    q = query.lower()
    comparison_markers = [
        " vs ",
        " versus ",
        " compare ",
        " comparison ",
        " which is better ",
        " better than ",
        " or ",
    ]
    return any(marker in q for marker in comparison_markers)


def build_search_tasks(query: str):
    q = query.strip()

    if not detect_comparison(q):
        return [task.strip() for task in re.split(r"\n+", q) if task.strip()]

    maybe_entities = re.split(
        r"\b(?:vs|versus|compare|comparison)\b", q, flags=re.IGNORECASE
    )
    entities = []
    for part in maybe_entities:
        clean = re.sub(r"[^a-zA-Z0-9\s-]", "", part).strip()
        if clean:
            entities.append(clean)

    if len(entities) < 2:
        entities = [q]

    tasks = []
    for entity in entities:
        entity_name = entity.strip()
        if entity_name:
            tasks.append(f"{entity_name} capabilities")
            tasks.append(f"{entity_name} pricing")
            tasks.append(f"{entity_name} performance and benchmarks")

    tasks = tasks[:6]
    tasks.append(f"{entities[0].strip()} vs {entities[1].strip()} use cases")
    return tasks


def create_plan(query):
    """
    Break a research query into smaller research tasks.
    """
    if detect_comparison(query):
        return "\n".join(
            f"{index}. {task}"
            for index, task in enumerate(build_search_tasks(query), start=1)
        )

    system_prompt = """
You are an expert AI Research Planner.

Your job is to break a user's research query into 3-5 executable search tasks.

Rules:
- Return ONLY the numbered research plan.
- Do NOT answer the user's question.
- Do NOT summarize.
- Do NOT write introductions or conclusions.
- Every task must be directly searchable on Google/Tavily.
- Keep tasks short and specific.

Example 1

User:
Explain LangGraph

Plan:
1. What is LangGraph
2. Core concepts of LangGraph
3. Nodes and edges
4. State management
5. Real-world use cases

Bad Tasks:
- Gather information
- Analyze findings
- Write a report

Good Tasks:
- Groq pricing
- Gemini benchmarks
- LangGraph state management
- ChromaDB setup
"""
    user_prompt = f"""
    Research Query:
    {query}

Generate the research plan.
"""

    response = model.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    return response.content


if __name__ == "__main__":
    query = input("Enter your research query: ")

    plan = create_plan(query)

    print("\nResearch Plan:\n")
    print(plan)

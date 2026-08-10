from typing import TypedDict, List


class ResearchState(TypedDict):
    query: str
    plan: str
    search_results: list
    sources: list
    documents: list
    draft_summary: str

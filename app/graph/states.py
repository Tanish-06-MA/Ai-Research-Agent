from typing import TypedDict, List


class ResearchState(TypedDict):
    query: str
    plan: str
    intent: str
    search_results: list
    sources: list
    documents: list
    draft_summary: str
    pdf_relevant: bool
    pdf_only: bool
    conversation_history: list

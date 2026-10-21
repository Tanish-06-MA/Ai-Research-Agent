from typing import TypedDict


class ResearchState(TypedDict):
    """
    Shared state for the AI Research Agent LangGraph workflow.

    Fields:
        query:                User's research query.
        plan:                 Generated research plan (numbered search tasks).
        intent:               Detected source routing — PDF_ONLY | WEB_ONLY | PDF_AND_WEB.
        search_results:       Web search results grouped by task.
        sources:              Collected source URLs from web search.
        documents:            Retrieved PDF chunks with content, source, and distance.
        draft_summary:        Final generated research report.
        pdf_relevant:         Whether relevant PDF chunks were found.
        conversation_history: Running conversation context as a string.
    """

    query: str
    plan: str
    intent: str
    search_results: list
    sources: list
    documents: list
    draft_summary: str
    pdf_relevant: bool
    conversation_history: str

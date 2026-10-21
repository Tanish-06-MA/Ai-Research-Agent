from datetime import datetime

from app.graph.graph_builder import app
from app.utils.pdf_generator import generate_pdf
from app.database.history import init_db, save_research, check_cache


def main():
    """
    CLI entry point for the AI Research Agent.

    Runs an interactive loop where users can ask research questions.
    Supports PDF-based retrieval, web search, or both based on intent detection.

    PDF reports are generated only when the user types 'save pdf',
    or automatically on exit if there is an unsaved report.
    """
    init_db()

    print("=" * 60)
    print("  AI Research Agent")
    print("=" * 60)
    print("  Commands:")
    print("    - Type your research query and press Enter")
    print("    - Type 'save pdf' to save the last report as PDF")
    print("    - Type 'exit' or 'quit' to end the session")
    print("    - Upload a PDF to chroma_db first for PDF queries")
    print("=" * 60)

    conversation_history = ""

    # Track the last report for save-on-demand and save-on-exit
    last_report = None
    last_query = None
    last_sources = []
    report_saved = True  # No unsaved report initially

    while True:
        try:
            query = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if not query:
            continue

        if query.lower() in ["exit", "quit"]:
            break

        # Handle "save pdf" command
        if query.lower() in ["save pdf", "save", "save report"]:
            if last_report and not report_saved:
                pdf_path = generate_pdf(last_report, last_query)
                if pdf_path:
                    print(f"\nPDF saved: {pdf_path}")
                    report_saved = True
                else:
                    print("\n[ERROR] Failed to generate PDF.")
            elif report_saved and last_report:
                print("\nLast report is already saved.")
            else:
                print("\nNo report to save yet. Ask a research query first.")
            continue

        # Check local SQLite cache first to minimize external API consumption
        cached = check_cache(query)
        if cached:
            cached_report, cached_sources_str, cached_pdf_path = cached
            print("\n[CACHE MATCH] Loading report from local database...")
            print("\nAssistant:\n")
            print(cached_report)

            # Store in active session variables for save-on-demand & memory
            last_report = cached_report
            last_query = query
            try:
                import ast
                last_sources = ast.literal_eval(cached_sources_str)
            except Exception:
                last_sources = []
            report_saved = bool(cached_pdf_path)

            conversation_history += f"\nUser: {query}\nAssistant: {cached_report}\n"
            continue

        try:
            result = app.invoke(
                {
                    "query": query,
                    "plan": "",
                    "search_results": [],
                    "sources": [],
                    "documents": [],
                    "draft_summary": "",
                    "conversation_history": conversation_history,
                    "intent": "",
                    "pdf_relevant": False,
                }
            )

            report = result["draft_summary"]

            print("\nAssistant:\n")
            print(report)

            # Get updated history from graph (updated in summarize_node only)
            conversation_history = result["conversation_history"]

            # Track last report for save-on-demand
            last_report = report
            last_query = query
            last_sources = result.get("sources", [])
            report_saved = False

            # Save to database (always — this is history, not PDF export)
            timestamp = datetime.now().isoformat()
            save_research(
                query=query,
                timestamp=timestamp,
                report=report,
                sources=str(last_sources),
                pdf_path="",
            )

        except KeyboardInterrupt:
            print("\n\nQuery cancelled.")
            continue
        except Exception as e:
            error_msg = str(e).lower()

            if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
                print("\n[ERROR] API rate limit exceeded. Please wait and try again.")
            elif "401" in str(e) or "403" in str(e) or "auth" in error_msg:
                print("\n[ERROR] API authentication failed. Check your API keys in .env")
            elif "connection" in error_msg or "timeout" in error_msg:
                print("\n[ERROR] Connection failed. Check your internet connection.")
            else:
                print(f"\n[ERROR] {e}")

            continue

    # Auto-save on exit if there's an unsaved report
    if last_report and not report_saved:
        print("Saving last report as PDF before exit...")
        pdf_path = generate_pdf(last_report, last_query)
        if pdf_path:
            print(f"PDF saved: {pdf_path}")

            # Update the database entry with the PDF path
            timestamp = datetime.now().isoformat()
            save_research(
                query=last_query,
                timestamp=timestamp,
                report=last_report,
                sources=str(last_sources),
                pdf_path=pdf_path,
            )

    print("Session ended.")


if __name__ == "__main__":
    main()

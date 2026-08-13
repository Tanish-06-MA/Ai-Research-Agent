from datetime import datetime

from app.graph.graph_builder import app
from app.utils.pdf_generator import generate_pdf
from app.database.history import init_db, save_research


def main():
    init_db()

    conversation_history = ""

    while True:
        query = input("\nYou: ").strip()

        if query.lower() in ["exit", "quit"]:
            print("Chat ended.")
            break

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

        # Get updated history from graph
        conversation_history = result["conversation_history"]

        # Generate PDF
        pdf_path = generate_pdf(report, query)

        print(f"\nPDF generated: {pdf_path}")

        # Save research history
        timestamp = datetime.now().isoformat()

        save_research(
            query=query,
            timestamp=timestamp,
            report=report,
            sources=str(result.get("sources", [])),
            pdf_path=pdf_path,
        )


if __name__ == "__main__":
    main()

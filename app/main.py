from datetime import datetime

from app.graph.graph_builder import app
from app.utils.pdf_generator import generate_pdf
from app.database.history import init_db, save_research


def main():
    # Initialize database
    init_db()

    query = input("Enter your Query: ")

    result = app.invoke(
        {
            "query": query,
            "plan": "",
            "search_results": [],
            "sources": [],
            "documents": [],
            "draft_summary": "",
        }
    )

    report = result["draft_summary"]

    print("\nResearch Report:\n")
    print(report)

    # Generate PDF
    pdf_path = generate_pdf(report, query)

    print(f"\nPDF generated: {pdf_path}")

    # Current timestamp
    timestamp = datetime.now().isoformat()

    # Save research history
    save_research(
        query=query,
        timestamp=timestamp,
        report=report,
        sources=str(result.get("sources", [])),
        pdf_path=pdf_path,
    )

    print("Research saved to history.")


if __name__ == "__main__":
    main()

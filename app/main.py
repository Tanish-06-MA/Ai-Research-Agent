from app.graph.graph_builder import app


def main():
    query = input("Enter your Query: ")

    result = app.invoke(
        {
            "query": query,
            "plan": "",
            "search_results": [],
            "sources": [],
            "draft_summary": "",
        }
    )

    print("\nResearch Plan:\n")
    print(result["plan"])


if __name__ == "__main__":
    main()

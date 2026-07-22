from app.tools.search import web_search
from app.llm.groq_client import generate_summary


def main():
    query = input("Enter your Query")

    search = web_search(query)

    summary = generate_summary(search)

    print(summary)


if __name__ == "__main__":
    main()

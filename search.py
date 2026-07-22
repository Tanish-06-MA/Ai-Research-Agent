from tavily import TavilyClient
import os
from dotenv import load_dotenv


load_dotenv()

api = os.environ.get("TAVILY_API")

tavily_client = TavilyClient(api)


def web_search(query: str):
    respose = tavily_client.search(query, max_results=2)

    result = respose.get("results", [])

    formatted = []
    for r in result:
        formatted.append(
            {"title": r["title"], "url": r["url"], "snippet": r["content"]}
        )

    return formatted


search = web_search("Who is iron Man")
print(search)

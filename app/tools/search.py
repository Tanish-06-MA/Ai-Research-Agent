from tavily import TavilyClient
import os
from dotenv import load_dotenv


load_dotenv()

api = os.environ.get("TAVILY_API")

tavily_client = TavilyClient(api)


def web_search(query: str) -> list:
    """
    Search the web using Tavily API.

    Returns a list of dicts with 'title', 'url', and 'snippet' keys.
    Returns an empty list on API failure or empty results.
    """
    try:
        response = tavily_client.search(query, max_results=2)

        results = response.get("results", [])

        formatted = []
        for r in results:
            print(f"TAVILY URL: {r['url']}")
            formatted.append(
                {"title": r["title"], "url": r["url"], "snippet": r["content"]}
            )

        return formatted

    except Exception as e:
        error_msg = str(e).lower()

        if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
            print("[ERROR] Tavily API rate limit exceeded. Skipping web search.")
        elif "401" in str(e) or "403" in str(e) or "auth" in error_msg:
            print("[ERROR] Tavily API authentication failed. Check your TAVILY_API key.")
        elif "timeout" in error_msg or "connection" in error_msg:
            print("[ERROR] Tavily API connection failed. Check your internet connection.")
        else:
            print(f"[ERROR] Web search failed: {e}")

        return []

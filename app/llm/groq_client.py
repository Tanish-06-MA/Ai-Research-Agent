from app.llm.prompts import SYSTEM_PROMPT
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API"))


def generate_summary(query, plan, search_results, documents):
    """
    Generate final research report from web search results
    and retrieved PDF documents.
    """

    prompt = f"""
User Query:
{query}

Research Plan:
{plan}

Search Results:
"""

    # Add web search results
    for task_data in search_results:
        task = task_data["task"]
        results = task_data["results"]

        prompt += f"\nResearch Task: {task}\n\n"

        if not results:
            prompt += "No search results found for this task.\n"
            continue

        for result in results:
            prompt += f"""
Title: {result.get("title", "Untitled")}

Snippet:
{result.get("snippet", "")}

Source:
{result.get("url", "No URL")}

---
"""

    # Add retrieved PDF chunks
    prompt += "\nPDF Documents:\n"

    if not documents:
        prompt += "No relevant PDF documents found.\n"
    else:
        for document in documents:
            prompt += f"""
PDF Content:
{document}

---
"""

    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    return chat_completion.choices[0].message.content

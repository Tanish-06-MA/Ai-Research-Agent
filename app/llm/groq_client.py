from app.llm.prompts import SYSTEM_PROMPT
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API"))


def generate_summary(query, search_results):

    prompt = f"""
User Query:
{query}

Search Results:

"""

    for results in search_results:
        for result in results:
            prompt += f"""
Title: {result["title"]}

Snippet: {result["snippet"]}

Source: {result["url"]}

---------------------------------
"""

    chat_completion = client.chat.completions.create(
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
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content

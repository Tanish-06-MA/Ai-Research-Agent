from app.llm.prompts import SYSTEM_PROMPT
import os
from app.llm.prompts import SYSTEM_PROMPT
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


client = Groq(api_key=os.environ.get("GROQ_API"))


def generate_summary(search_results):
    """
    Takes search results from Tavily and returns
    an AI-generated summary.
    """

    prompt = "Summarize the following search results:\n\n"

    for result in search_results:
        prompt += f"""
Title: {result["title"]}

Snippet: {result["snippet"]}

Source: {result["url"]}

-----------------------------------
"""
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {"role": "user", "content": prompt},
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content

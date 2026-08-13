import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(override=True)

api = os.environ.get("GEMINI_API_KEY")

model = ChatOpenAI(
    model="gemini-3.5-flash",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=api,
)


def detect_intent(
    query: str,
    conversation_history: str = "",
    has_pdf: bool = False,
    relevant_pdf_chunks: int = 0,
) -> str:

    system_prompt = """
You are the source-routing controller of an AI research assistant.

Your job is to decide where the assistant should get information from.

You MUST return exactly ONE of:

PDF_ONLY
WEB_ONLY
PDF_AND_WEB

Rules:

1. If the user explicitly says NOT to search the web,
   return PDF_ONLY if a PDF is available.
   Never return WEB_ONLY.

2. If the user explicitly asks about an uploaded PDF,
   uploaded document, paper, or previous answer that came from the PDF,
   prefer PDF_ONLY.

3. If the user asks for current, latest, today's, recent,
   live, online, or web information,
   prefer WEB_ONLY.

4. If the user explicitly asks to compare the uploaded PDF
   with external/web information, return PDF_AND_WEB.

5. Use conversation history to understand references such as:
   "this", "that", "it", "the result", "explain simply",
   "what does this mean", etc.

6. If the current query is a follow-up to a previous PDF-related
   discussion, use PDF_ONLY unless the user asks for web/current
   information.

7. Do NOT decide based only on individual keywords.
   Understand the meaning of the complete query.

8. If a PDF exists and the question is related to the current
   conversation topic, prefer PDF_ONLY.

9. If there is no PDF available, return WEB_ONLY.

10. Return ONLY the intent label.
"""

    user_prompt = f"""
Current user query:
{query}

Conversation history:
{conversation_history if conversation_history else "No previous conversation."}

PDF available:
{has_pdf}

Relevant PDF chunks:
{relevant_pdf_chunks}

Choose exactly one:
PDF_ONLY
WEB_ONLY
PDF_AND_WEB
"""

    response = model.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    intent = response.content.strip().upper()

    if intent not in {"PDF_ONLY", "WEB_ONLY", "PDF_AND_WEB"}:
        return "WEB_ONLY"

    return intent

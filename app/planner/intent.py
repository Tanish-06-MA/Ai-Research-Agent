import os
import json
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv(override=True)

api = os.environ.get("OPENROUTER_API_KEY")

model = ChatOpenAI(
    model="openai/gpt-oss-20b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=api,
)


def parse_json_response(content: str) -> dict:
    """
    Safely extract and parse JSON from the LLM response.
    Supports raw JSON, markdown-wrapped json, or general curly brace matching.
    """
    cleaned = content.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try matching ```json ... ``` blocks
    match = re.search(r"```json\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try matching first { to last }
    match = re.search(r"({.*})", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    return {}


def detect_intent(
    query: str,
    conversation_history: str = "",
    has_pdf: bool = False,
    relevant_pdf_chunks: int = 0,
) -> tuple[str, str]:
    """
    Detect the source routing intent and generate the search plan in a single API call.

    Returns:
        A tuple of (intent_label, plan_text).
        - intent_label: "PDF_ONLY" | "WEB_ONLY" | "PDF_AND_WEB"
        - plan_text: Numbered list of search tasks, or empty string.
    """
    system_prompt = """
You are the central controller of an AI research assistant.
Your job is to decide where the assistant should retrieve information from, and (if web search is needed) create a research plan.

You MUST respond with a JSON object containing EXACTLY two fields:
{
  "intent": "PDF_ONLY" | "WEB_ONLY" | "PDF_AND_WEB",
  "plan": "A numbered list of 3-5 specific search tasks, or empty string if PDF_ONLY."
}

DECISION RULES FOR INTENT (apply in order):

1. NO PDF AVAILABLE:
   - If "PDF available" is False → intent MUST be WEB_ONLY.

2. EXPLICIT PDF REFERENCE:
   - If the user mentions "uploaded PDF", "the paper", "the document", "from the PDF", or similar → intent is PDF_ONLY.
   - Unless they ALSO ask for web/external/current comparison → then PDF_AND_WEB.

3. EXPLICIT WEB/CURRENT REQUEST:
   - If the user asks for "latest", "current", "recent", "today's", "live", "online", "new research" without referencing the PDF → intent is WEB_ONLY.
   - If they ask for latest/current AND reference the PDF → intent is PDF_AND_WEB.

4. COMPARISON OR AUGMENTATION:
   - If the user asks to "compare the PDF with", "augment with web", or similar → intent is PDF_AND_WEB.

5. FOLLOW-UP QUESTIONS & CONTEXTUAL VARIABLES:
   - If the previous discussion was about PDF content, and the current query is a follow-up (e.g. "explain this simply", "summarize that") OR asks about specific mathematical terms, equations, variables, or functions (e.g. "what is F(x)?", "what does H(x) mean?", "what is x?") that relate to the ongoing PDF topic → intent is PDF_ONLY.
   - If the previous discussion was about web results, and the current query is a follow-up → intent is WEB_ONLY.

RULES FOR RESEARCH PLAN:
- Only generate a plan if intent is WEB_ONLY or PDF_AND_WEB.
- Break the user's research query into 3-5 specific, numbered search tasks (e.g. "1. Task 1\n2. Task 2...").
- Keep tasks short, specific, and search-engine optimized (e.g. "Groq pricing", "LangGraph state management").
- Do NOT write introductions or conclusions.
- If intent is PDF_ONLY, set "plan" to "".

CRITICAL: Return ONLY valid JSON. Do not include any explanations.
"""

    user_prompt = f"""
Current user query:
{query}

Conversation history:
{conversation_history if conversation_history else "No previous conversation."}

PDF available:
{has_pdf}

Relevant PDF chunks found:
{relevant_pdf_chunks}

Return JSON with "intent" and "plan".
"""

    try:
        response = model.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]
        )

        parsed = parse_json_response(response.content)

        intent = parsed.get("intent", "").strip().upper()
        plan = parsed.get("plan", "").strip()

        # Sanitize intent
        valid_intents = {"PDF_ONLY", "WEB_ONLY", "PDF_AND_WEB"}
        if intent not in valid_intents:
            # Fallback search inside intent text
            found = False
            for valid in valid_intents:
                if valid in intent:
                    intent = valid
                    found = True
                    break
            if not found:
                intent = "PDF_ONLY" if has_pdf else "WEB_ONLY"

        # Hard constraint fallback
        if not has_pdf:
            intent = "WEB_ONLY"

        if intent == "PDF_ONLY":
            plan = ""

        # If plan is missing for web search, generate a basic default
        if intent in ("WEB_ONLY", "PDF_AND_WEB") and not plan:
            plan = f"1. {query}"

        return intent, plan

    except Exception as e:
        error_msg = str(e).lower()
        if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
            print(f"[ERROR] Rate limit exceeded. Falling back to default routing.")
        else:
            print(f"[ERROR] Intent/Planning failed: {e}")

        # Fallback values
        fallback_intent = "PDF_ONLY" if has_pdf else "WEB_ONLY"
        fallback_plan = "" if fallback_intent == "PDF_ONLY" else f"1. {query}"
        return fallback_intent, fallback_plan

import os
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


def create_plan(query):
    """
    Break a research query into smaller reserch tasks.
    """

    system_prompt = """
   You are an expert research planner.

Your job is to break a user's research query into 3-5 clear research tasks.

Rules:
- Break the query into logical research steps.
- Each task should be specific and concise.
- Return ONLY the numbered research plan.
- Do not answer the user's question.
    """
    user_prompt = f"""
    Research Query:
    {query}

Create a research plan.
"""

    response = model.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    return response.content


if __name__ == "__main__":
    query = input("Enter your research query: ")

    plan = create_plan(query)

    print("\nResearch Plan:\n")
    print(plan)

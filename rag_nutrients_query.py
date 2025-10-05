from agents import Agent, Runner, trace, function_tool
import chromadb
from utils.app_config import AppConfig
import asyncio

# load the environment
_ = AppConfig()

chroma_client = chromadb.PersistentClient(path="chroma")
calories_db = chroma_client.get_collection(name="nutrition_db")
nutrition_qna_db = chroma_client.get_collection(name="nutrition_qna")

@function_tool
def calorie_lookup_tool(query: str, max_results: int = 3) -> str:
    """
    Tool function too look up calorie information.

    Args:
        query: The food item to look up.
        max_results: The maximum number of results to return.

    Returns:
        A string containing the nutrition information.
    """

    results = calories_db.query(query_texts=[query], n_results=max_results)

    if not results["documents"][0]:
        return f"No nutrition information found for: {query}"

    # Format results for the agent
    formatted_results = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        food_item = metadata["food_item"].title()
        calories = metadata["calories_per_100g"]
        category = metadata["food_category"].title()

        formatted_results.append(
            f"{food_item} ({category}): {calories} calories per 100g"
        )

    return "Nutrition Information:\n" + "\n".join(formatted_results)

@function_tool
def nutrtition_qna_tool(query: str, max_results: int = 3) -> str:
    """
    Tool function to ask a question about nutrition.

    Args:
        query: The question to ask
        max_results: The maximum number of results to return.

    Returns:
        A string containing the question and the answer related to the query.
    """

    results = nutrition_qna_db.query(query_texts=[query], n_results=max_results)

    if not results["documents"][0]:
        return f"No information found for: {query}"

    # Format results for the agent
    formatted_results = []
    for i, doc in enumerate(results["documents"][0]):
        formatted_results.append(doc)

    return "Related answers to your question:\n" + "\n".join(formatted_results)


calorie_agent = Agent(
    name="Nutrition Assistant",
    instructions="""
    You are a helpful nutrition assistant giving out calorie information and nutrtion advice    .
    You give concise answers.

    If you need to look up calorie information, use the calorie_lookup_tool.
    If are asked a question about nutrition, always use the nutrtition_qna_tool first to see if there is an answer in the knowledge base.
    """,
    tools=[calorie_lookup_tool, nutrtition_qna_tool],
)

async def main():
    with trace("Nutrition Assistant with Nutrition and Calorie RAG"):
        result = await Runner.run(
            calorie_agent,
            "What are the best meal choices for pregnant women and how many calories do they have?"
        )
        print(result.final_output)

if __name__ == "__main__":
    #execute the agent
    asyncio.run(main())

import chromadb
from agents import Agent, Runner, function_tool, trace
from agents.mcp import MCPServerStreamableHttp
from utils.app_config import AppConfig
import asyncio
import sys
import contextlib
import io

# load the environment
config = AppConfig()

chroma_client = chromadb.PersistentClient(path="chroma")
nutrition_db = chroma_client.get_collection(name="nutrition_db")

@function_tool
def calorie_lookup_tool(query: str, max_results: int = 3) -> str:
    """
    Tool function for a RAG database to look up calorie information for specific food items, but not for meals.

    Args:
        query: The food item to look up.
        max_results: The maximum number of results to return.

    Returns:
        A string containing the nutrition information.
    """

    results = nutrition_db.query(query_texts=[query], n_results=max_results)

    if not results["documents"][0]:
        return f"No nutrition information found for: {query}"

    # Format results for the agent
    formatted_results = []
    for i, doc in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]
        food_item = metadata["food_item"].title() #title is built in method in string that capitalizes first letter of each word
        calories = metadata["calories_per_100g"]
        category = metadata["food_category"].title()

        formatted_results.append(
            f"{food_item} ({category}): {calories} calories per 100g"
        )

    return "Nutrition Information:\n" + "\n".join(formatted_results)


# Exa Search MCP code comes here:
exa_search_mcp = MCPServerStreamableHttp(
    name="Exa Search MCP",
    params={
        "url": f"https://mcp.exa.ai/mcp?exaApiKey={config.get_exa_api_key()}",
        "timeout": 30,
    },
    client_session_timeout_seconds=30,
    cache_tools_list=True,
    max_retry_attempts=1,
)

#agent that has a tool and an mcp server
calorie_agent_with_search = Agent(
    name="Nutrition Assistant",
    instructions="""
    * You are a helpful nutrition assistant giving out calorie information.
    * You give concise answers.
    * You follow this workflow:
        0) First, use the calorie_lookup_tool to get the calorie information of the ingredients. But only use the result if it's explicitly for the food requested in the query.
        1) If you couldn't find the exact match for the food or you need to look up the ingredients, search the EXA web to figure out the exact ingredients of the meal.
        Even if you have the calories in the web search response, you should still use the calorie_lookup_tool to get the calorie
        information of the ingredients to make sure the information you provide is consistent.
        2) Then, if necessary, use the calorie_lookup_tool to get the calorie information of the ingredients.
    * Even if you know the recipe of the meal, always use Exa Search to find the exact recipe and ingredients.
    * Once you know the ingredients, use the calorie_lookup_tool to get the calorie information of the individual ingredients.
    * If the query is about the meal, in your final output give a list of ingredients with their quantities and calories for a single serving. Also display the total calories.
    * Don't use the calorie_lookup_tool more than 10 times.
    """,
    tools=[calorie_lookup_tool],
    mcp_servers = [exa_search_mcp]
)

"""
To verify the traces for an api key go to 
https://platform.openai.com/logs?api=traces
You will find workflows. Name of the workflow
will be what you pass in with trace() statement.
Click on work flow and you will see the details of
what tools/mcps were called.  For e.g,
when user asks the question 
How many calories are in an english breakfast?
agent decides to use ExaWebsearch to find out the ingredients
for an english break fast and then make a call to 
calories_lookup_tool for each ingredient , sums up total calories 
and gives the final response. Wow that's awesome
"""
async def main():

    # connect to mcp server
    await exa_search_mcp.connect()

    question1 = "How many calories are in total in a banana and an apple? Also give calories per 100g"
    question2 = "How many calories are in an english breakfast?"

    #This search will not involve mcp
    with trace("Nutrition Assistant with MCP - Only uses calorie_lookup_tool"):

        print(f"Answering question1:{question1}")

        result = await Runner.run(
            calorie_agent_with_search,
            question1
        )
        print(result.final_output)

    #This search will involve mcp
    with trace("Nutrition Assistant with MCP"):
        print(f"Answering question2:{question2}")

        result = await Runner.run(
            calorie_agent_with_search,
            question2
        )
        print(result.final_output)

if __name__ == "__main__":
    # Suppress the expected async cleanup warning from MCP client disconnection
    # This occurs when the cancel scope is exited in a different task than it was entered,
    # which is normal behavior for HTTP streaming connections and doesn't affect functionality.
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            asyncio.run(main())
        except Exception as e:
            # Re-raise any unexpected errors
            raise
    
    print("MCP client disconnected successfully (cleanup warning suppressed)") 
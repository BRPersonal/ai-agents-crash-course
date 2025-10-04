from agents import Agent, ModelSettings, Runner, function_tool, trace
from utils.app_config import AppConfig
import asyncio

# load the environment
_ = AppConfig()

@function_tool
def get_food_calories(food_item: str) -> str:
    """
    Get calorie information for common foods to help with nutrition tracking.

    Args:
        food_item: Name of the food (e.g., "apple", "banana")

    Returns:
        Calorie information per standard serving
    """
    # Simple calorie database - in real world, you'd use USDA API
    calorie_data = {
        "apple": "80 calories per medium apple (182g)",
        "banana": "105 calories per medium banana (118g)",
        "broccoli": "25 calories per 1 cup chopped (91g)",
        "almonds": "164 calories per 1oz (28g) or about 23 nuts",
    }

    food_key = food_item.lower()
    if food_key in calorie_data:
        return f"{food_item.title()}: {calorie_data[food_key]}"
    else:
        return f"I don't have calorie data for {food_item} in my database. Try common foods like apple, banana or rice."

#Create calorie agent with our tool. Optionally we could force the tool choice as well
calorie_agent = Agent(
    name="Nutrition Assistant",
    instructions="""
    You are a helpful nutrition assistant giving out calorie information.
    You give concise answers.
    """,
    tools=[get_food_calories]
    # model_settings=ModelSettings(tool_choice="get_food_calories")
)

async def main():
    with trace("Nutrition Assistant with tools"):
        result = await Runner.run(
            calorie_agent, "How many calories are in total in a banana and an apple?"
        )
        print(result.final_output)

if __name__ == "__main__":
    #execute the agent
    asyncio.run(main())

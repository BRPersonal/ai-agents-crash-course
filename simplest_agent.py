from openai import OpenAI
import os
import asyncio
from utils.app_config import AppConfig
from agents import Agent, Runner, trace
from openai.types.responses import ResponseTextDeltaEvent

# load the environment
config = AppConfig()

# Test OpenAI Access
print(
    OpenAI()
    .responses.create(
        model=config.get_open_ai_default_model(), input="Say: We are up and running!"
    )
    .output_text
)

# Create a simple Nutrition Assistant Agent
nutrition_agent = Agent(
    name="Nutrition Assistant",
    instructions="""
    You are a helpful assistant giving out nutrition advice.
    You give concise answers.
    """,
)

async def main(streaming_response:bool = False):
    with trace("Simple Nutrition Agent"):
        if streaming_response:
            response_stream = Runner.run_streamed(nutrition_agent, "How healthy are bananas?")
            async for event in response_stream.stream_events():
                if event.type == "raw_response_event" and isinstance(
                        event.data, ResponseTextDeltaEvent
                ):
                    print(event.data.delta, end="", flush=True)
        else:
            result = await Runner.run(nutrition_agent, "How healthy are bananas?")
            print(result)

if __name__ == "__main__":
    #execute the agent
    choice = input("Streaming Response (y/n):")
    asyncio.run(main(choice.lower() == "y"))

from openai import OpenAI
import asyncio
from agents import Agent, Runner, trace
from openai.types.responses import ResponseTextDeltaEvent
from utils.config import settings


# Test OpenAI Access
print(
    OpenAI()
    .responses.create(
        model=settings.OPENAI_DEFAULT_MODEL, input="Say: We are up and running!"
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

async def main(question:str,streaming_response:bool = False):
    print(f"Question: {question}")
    
    with trace("Simple Nutrition Agent"):
        if streaming_response:
            response_stream = Runner.run_streamed(nutrition_agent, question)
            async for event in response_stream.stream_events():
                if event.type == "raw_response_event" and isinstance(
                        event.data, ResponseTextDeltaEvent
                ):
                    print(event.data.delta, end="", flush=True)
        else:
            result = await Runner.run(nutrition_agent, question)
            print(result.final_output)

if __name__ == "__main__":
    #execute the agent
    question = "How healthy are bananas?"
    choice = input("Streaming Response (y/n):")
    asyncio.run(main(question,choice.lower() == "y"))

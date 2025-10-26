#just import is enough to load the environment keys 
from utils.config import settings 
from agents import Agent, Runner
import asyncio

# Create a simple Nutrition Assistant Agent
my_agent = Agent(
    name="AI Assistant",
    instructions="""
    You are a helpful assistant anwering user queries
    """,
)

async def main(question:str):
    print(f"Question: {question}")
    result = await Runner.run(my_agent, question)
    print(result.final_output)

if __name__ == "__main__":
  question = """
              I went to the market and bought 10 apples. I gave 2 apples to the neighbor and 2
              to the repairman. I then went and bought 5 more apples and ate 1. How many apples
              did I remain with?
              Let's think step by step
              """
  asyncio.run(main(question))
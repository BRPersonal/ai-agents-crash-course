from agents import Agent, Runner, SQLiteSession, trace
import asyncio
import contextlib
import io
from utils.config import settings

nutrition_agent = Agent(
    name="Nutrition Assistant",
    instructions="""
    You are a helpful assistant comparing how healthy different foods are.
    If you answer, give a list of how healthy the foods are with a score from 1 to 10. Order by: healtiest food comes first.

    Example:
    Q: Compare X and Y
    A: X is healtier as Y.
    1) X: 8/10 - Very healthy but high in fructose
    2) Y: 3/10 - High in sugar and fat
    """,
)

async def main(add_memory:bool):
  """
  By default agents are stateless. Every invocation of run()
  starts a new conversation. No history is maintained. 
  IF agent has to rememerb previous conversation, we need to pass a session
  """

  session = None
  if add_memory:
    session = SQLiteSession("conversation_history")

  result = await Runner.run(nutrition_agent, 
                  "Which is healthier, bananas or lollipop?",
                  session = session)
  print(result.final_output)

  input("Press enter to continue...")
  result = await Runner.run(nutrition_agent, 
                    "Add apples to the comparison",
                    session=session)
  print(result.final_output)    

if __name__ == "__main__":
  answer = input("Use memory(y/n)?")
  asyncio.run(main(answer == "y" or answer == "Y"))


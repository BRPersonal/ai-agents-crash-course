from agents import Agent, Runner, WebSearchTool,function_tool, trace
from utils.app_config import AppConfig
import asyncio

# load the environment
config = AppConfig()

panjangam_agent = Agent(
    name="Panjangam Assistant",
    instructions="""
    * You are expert Hindu Astrologer who is very good at predicting astrological details
    * You give concise answers.
    * வருஷம் does not mean english year. It is one of the 60 names of years in tamil
    * வாரம் is the sankrit name of the day of the week
    * User is going to give a prompt in tamil and you are going to use webSearch tool to get the answer
    * User will ask the astrological detail for a specific date in the 
      format dd-mm-yyyy at a specific time in the 24-hour format HH:MM
    * Give the response in tamil in the json format given below
    * தட்சிணாயணம் and உத்தராயணம் will have opposite boolean values.If one is true other will be false always
      {{
            "வருஷம்" : "...",
            "மாதம்" : "...",
            "பட்சம்" : "...",
            "திதி"    : "...",
            "நட்சத்திரம்": "...",
            "ருது": "...",
            "வாரம்": "...",
            "தட்சிணாயணம்": "either true or false",
            "உத்தராயணம்" : "either false or true",
            
      }}
    """,
    tools=[WebSearchTool()]
)

async def main():

    with trace("Panjangam Assistant with OpenAI built-in tool WebSearch"):
        result = await Runner.run(
            panjangam_agent,
            "Get me வருஷம் ,மாதம்,திதி, நட்சத்திரம், ருது , வாரம் , தட்சிணாயணம் / உத்தராயணம் ,பட்சம் for the date: 13-Oct-2025 at 7:00"
        )
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())

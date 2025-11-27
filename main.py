import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types
import asyncio

# Load environment variables
load_dotenv()

# Setup API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("🚫 GOOGLE_API_KEY not found in .env file!")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

print("✅ Gemini API key setup complete.")

# Define the agent
root_agent = Agent(
    name="helpful_assistant",
    model="gemini-2.5-flash-lite",
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

print("✅ Root Agent defined.")

# Runner
runner = InMemoryRunner(agent=root_agent)
print("✅ Runner created.")


async def run_agent():
    response = await runner.run_debug("What is Agent Development Kit from Google? What languages is it available in?")
    texts = [r.output_text for r in response if hasattr(r, "output_text")]
    print("\n".join(texts))

if __name__ == "__main__":
    asyncio.run(run_agent())

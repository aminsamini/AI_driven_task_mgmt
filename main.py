import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import google_search
from google.genai import types
import asyncio
import sqlalchemy
from google.adk.sessions import DatabaseSessionService

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

# Setup Database Session Service
session_service = DatabaseSessionService("sqlite:///task_management.db")
print("✅ Database Session Service created.")

# Runner
runner = Runner(agent=root_agent, session_service=session_service, app_name="task_management_system")
print("✅ Runner created.")


async def run_agent():
    # Using a fixed session ID for demonstration/testing persistence
    session_id = "test_session_001"
    
    while True:
        user_input = input("How can I help you? (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        if not user_input.strip():
            continue

        response = await runner.run_debug(user_input, session_id=session_id)
        texts = [r.output_text for r in response if hasattr(r, "output_text")]
        print("\n".join(texts))

if __name__ == "__main__":
    asyncio.run(run_agent())

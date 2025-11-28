from google.adk.agents import Agent
from google.adk.tools import google_search
from memory_tool import save_user_info

def create_root_agent():
    """Defines and returns the root agent."""
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash-lite",
        description="A simple agent that can answer general questions.",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search, save_user_info],
    )
    print("✅ Root Agent defined.")
    return root_agent

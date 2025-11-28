from google.adk.agents import Agent
from google.adk.tools import google_search

def create_root_agent():
    """Creates and returns the root agent."""
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash-lite",
        description="its a agent that can answer general questions and assist to use tools",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search],
    )
    print("✅ Root Agent defined.")
    return root_agent

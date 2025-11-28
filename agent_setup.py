from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.function_tool import FunctionTool
from memory_tool import save_user_info

def create_root_agent():
    """Defines and returns the root agent."""
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash-lite",
        description="A simple agent that can answer general questions.",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure. When saving user info using the save_user_info tool, you must extract the user's ID from the prompt and provide it as the 'user_id' argument.",
        tools=[google_search, FunctionTool(save_user_info)],
    )
    print("✅ Root Agent defined.")
    return root_agent

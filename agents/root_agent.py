from google.adk.agents import Agent
from google.adk.tools import google_search

def create_root_agent():
    """Creates the main agent with task creation capabilities."""
    root_agent = Agent(
        name="helpful_assistant",
        model="gemini-2.5-flash-lite",
        description="A helpful assistant that can answer questions, search the web, and create tasks using AI",
        instruction="""
You are a helpful assistant for an AI-powered task management system.

TASK CREATION:
When a user's message starts with "/task", the system will automatically handle the task creation process.
You do not need to call any specific tool for this, as it is handled by the application layer.
Just be aware that users might use this command.

GENERAL ASSISTANCE:
For other queries:
- Answer questions using your knowledge
- Use Google Search for current information
- Be helpful, friendly, and concise

Always provide clear, actionable responses.
""",
        tools=[google_search]
    )
    print("✅ Root Agent created with task creation capabilities")
    return root_agent

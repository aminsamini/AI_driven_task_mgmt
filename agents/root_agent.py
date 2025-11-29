from google.adk.agents import Agent
from google.adk.tools import google_search
from tools.task_tools import create_task_with_ai

def create_root_agent():
    """Creates the main agent with task creation capabilities."""
    root_agent = Agent(
        name="helpful_assistant",
        model=Gemini(model="gemini-2.0-flash-exp"),
        description="A helpful assistant that can answer questions, search the web, and create tasks using AI",
        instruction="""
You are a helpful assistant for an AI-powered task management system.

TASK CREATION:
When a user's message starts with "/task", extract the task description and create a task using the create_task_with_ai tool.

Example:
User: "/task Fix the login bug on the homepage"
You: *use create_task_with_ai tool with description "Fix the login bug on the homepage"*

For task creation:
1. Extract the description after "/task"
2. Call create_task_with_ai with the description
3. Report back the results to the user in a friendly way

GENERAL ASSISTANCE:
For other queries:
- Answer questions using your knowledge
- Use Google Search for current information
- Be helpful, friendly, and concise

Always provide clear, actionable responses.
""",
        tools=[google_search, create_task_with_ai]
    )
    print("✅ Root Agent created with task creation capabilities")
    return root_agent

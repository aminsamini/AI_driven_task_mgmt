import json
from google.adk.tools.tool import tool, ToolContext
from database import get_long_term_memory, update_long_term_memory

@tool
def save_user_info(tool_context: ToolContext, key: str, value: str) -> str:
    """
    Saves a key-value pair of information about the user for long-term memory.
    Use this tool to remember important, persistent facts about the user,
    such as their name, location, or preferences.

    Args:
        key: The key of the information to save (e.g., "name").
        value: The value of the information to save (e.g., "Alex").

    Returns:
        A confirmation message indicating the information has been saved.
    """
    session = tool_context.session
    user_id = session.state.get("user_id") if session else None

    if not user_id:
        return "Error: Could not save information. User is not logged in."

    memory = get_long_term_memory(user_id)
    memory[key] = value
    update_long_term_memory(user_id, memory)

    return f"Okay, I've saved that {key} is {value}."

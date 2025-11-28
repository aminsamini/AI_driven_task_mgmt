import json
from database import get_long_term_memory, update_long_term_memory

def save_user_info(user_id: str, key: str, value: str) -> str:
    """
    Saves a key-value pair of information about the user for long-term memory.
    Use this tool to remember important, persistent facts about the user,
    such as their name, location, or preferences.

    Args:
        user_id: The ID of the user.
        key: The key of the information to save (e.g., "name").
        value: The value of the information to save (e.g., "Alex").

    Returns:
        A confirmation message indicating the information has been saved.
    """
    if not user_id:
        return "Error: Could not save information. User is not logged in."

    memory = get_long_term_memory(user_id)
    memory[key] = value
    update_long_term_memory(user_id, memory)

    return f"Okay, I've saved that {key} is {value}."

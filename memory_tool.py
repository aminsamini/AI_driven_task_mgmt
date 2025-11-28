import json
from database import get_long_term_memory, update_long_term_memory
from tool_schemas import SaveUserInfoArgs

def save_user_info(args: SaveUserInfoArgs) -> str:
    """
    Saves a key-value pair of information about the user for long-term memory.
    Use this tool to remember important, persistent facts about the user,
    such as their name, location, or preferences.

    Args:
        args: A Pydantic model containing the user_id, key, and value.
    """
    if not args.user_id:
        return "Error: Could not save information. User is not logged in."

    memory = get_long_term_memory(args.user_id)
    memory[args.key] = args.value
    update_long_term_memory(args.user_id, memory)

    return f"Okay, I've saved that {args.key} is {args.value}."

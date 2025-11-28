import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_environment():
    """Sets up the environment variables and API keys."""
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    if not GOOGLE_API_KEY:
        raise ValueError("🚫 GOOGLE_API_KEY not found in .env file!")

    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
    
    print("✅ Gemini API key setup complete.")

def get_session_timeout():
    """Returns the session timeout in minutes."""
    return int(os.environ.get("SESSION_TIMEOUT", 30))

import os
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.tools import google_search
import asyncio
from google.adk.sessions import DatabaseSessionService
from database import init_db
import auth
import uuid
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Initialize the database
init_db()

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

async def handle_authentication():
    """Handles the user authentication flow."""
    while True:
        print("Do you have an account? (yes/no): ", end='', flush=True)
        has_account = sys.stdin.readline().strip().lower()
        
        if has_account == 'yes':
            try:
                print("Email: ", end='', flush=True)
                email = sys.stdin.readline().strip()
                print("Password (visible): ", end='', flush=True)
                password = sys.stdin.readline().strip()
                user = auth.authenticate_user(email, password)
                if user:
                    print(f"Welcome back, {user.first_name}!")
                    return user
                else:
                    print("Invalid credentials. Please try again.")
            except auth.RateLimitException as e:
                print(e)
        elif has_account == 'no':
            print("Let's create an account for you.")
            print("First Name: ", end='', flush=True)
            first_name = sys.stdin.readline().strip()
            print("Last Name: ", end='', flush=True)
            last_name = sys.stdin.readline().strip()
            print("Email: ", end='', flush=True)
            email = sys.stdin.readline().strip()
            while True:
                try:
                    print("Password (visible): ", end='', flush=True)
                    password = sys.stdin.readline().strip()
                    print("Confirm Password (visible): ", end='', flush=True)
                    password_confirm = sys.stdin.readline().strip()
                    if password == password_confirm:
                        user = auth.create_user(first_name, last_name, email, password)
                        print(f"Account created successfully! Welcome, {user.first_name}!")
                        return user
                    else:
                        print("Passwords do not match. Please try again.")
                except ValueError as e:
                    print(e)
                    if "Email already registered" in str(e):
                        print("Email: ", end='', flush=True)
                        email = sys.stdin.readline().strip()
                    continue
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")


async def run_agent():
    """Main function to run the agent after authentication."""
    user = await handle_authentication()
    if not user:
        return

    session_id = str(uuid.uuid4())
    print(f"New session started: {session_id}")

    while True:
        session = await session_service.get_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
        if session:
            timeout = int(os.environ.get("SESSION_TIMEOUT", 30))
            if datetime.utcnow() > session.update_time + timedelta(minutes=timeout):
                print("Your session has expired. Please log in again.")
                await session_service.delete_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
                break

        print("type or write 'exit' to quit : ", end='', flush=True)
        user_input = sys.stdin.readline().strip()
        
        if user_input.lower() in ["exit", "quit"]:
            await session_service.delete_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
            print("Session ended. Goodbye!")
            break

        if not user_input:
            continue

        response = await runner.run_debug(f"User '{user.id}' says: {user_input}", session_id=session_id)
        if session:
            session.state['user_id'] = user.id
            await session_service.update_session(session=session)

        texts = [r.output_text for r in response if hasattr(r, "output_text")]
        print("\n".join(texts))


if __name__ == "__main__":
    asyncio.run(run_agent())

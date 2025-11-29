import asyncio
import uuid
from datetime import datetime, timedelta
from google.adk.runners import Runner
from database import init_db
import config
from agents import create_root_agent, create_job_description_agent
from agents.task_agents import TaskCreationWorkflow
from tools.task_interaction import handle_show_my_tasks
import session_manager
import cli
from google.adk.sessions import InMemorySessionService

# Setup environment
config.setup_environment()

# Initialize database
init_db()

# Setup Agent, Session Service, and Runner
root_agent = create_root_agent()
job_description_agent = create_job_description_agent()

session_service = session_manager.create_session_service()
runner = Runner(agent=root_agent, session_service=session_service, app_name="task_management_system")
job_description_runner = Runner(agent=job_description_agent, session_service=InMemorySessionService(), app_name="job_desc_gen")

print("✅ Runner created.")
print("🎯 AI TASK MANAGEMENT SYSTEM")
print("=" * 60)
print("\nCommands:")
print("  /task <description>  - Create a new task with AI assistance")
print("  /show_my_tasks       - View and manage your tasks interactively")
print("  /help                - Show this help message")
print("  /exit or /quit       - Exit the application")
print("\nExamples:")
print("  /task Fix the authentication bug in the login module")
print("  /task Prepare Q4 financial report with charts and analysis")
print("  What's the weather today?")
print("=" * 60 + "\n")

async def generate_job_description(position):
    """Generates a job description using the AI agent."""
    response = await job_description_runner.run_debug(f"Write a job description for: {position}")
    
    # Extract text from response
    texts = []
    for event in response:
        # Check if event has content and parts
        if hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    texts.append(part.text)
    
    return "\n".join(texts).strip()

async def run_agent():
    """Main function to run the agent after authentication."""
    user = await cli.handle_authentication(job_description_generator=generate_job_description)
    if not user:
        return

    last_session = session_manager.get_last_session(user.id)
    session_id = None

    if last_session:
        choice = cli.prompt_session_choice(last_session)
        if choice == 'resume':
            session_id = last_session['id']
            print(f"Resuming session: {session_id}")
        else:
            session_id = str(uuid.uuid4())
            print(f"New session started: {session_id}")
    else:
        session_id = str(uuid.uuid4())
        print(f"New session started: {session_id}")

    while True:
        session = await session_service.get_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
        
        # Explicitly set user_id on the session object and update it
        if session:
            session.user_id = user.id
            await session_service.update_session(session=session)

        if session:
            timeout = config.get_session_timeout()
            if datetime.utcnow() > session.update_time + timedelta(minutes=timeout):
                cli.print_output("Your session has expired. Please log in again.")
                await session_service.delete_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
                break

        user_input = cli.get_user_input("type or write 'exit' to quit : ")
        
        if user_input.lower() in ["exit", "quit"]:
            await session_service.delete_session(session_id=session_id, user_id=user.id, app_name="task_management_system")
            cli.print_output("Session ended. Goodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith("/task"):
            task_description = user_input[5:].strip()
            if not task_description:
                cli.print_output("Please provide a task description after /task.")
                continue
            
            cli.print_output("Initializing Task Creation Agents...")
            workflow = TaskCreationWorkflow(user.id)
            result = await workflow.run(task_description)
            cli.print_output(result)
            continue

        if user_input == "/show_my_tasks":
            handle_show_my_tasks(user.id)
            continue

        if user_input == "/help":
            print("\nCommands:")
            print("  /task <description>  - Create a new task with AI assistance")
            print("  /show_my_tasks       - View and manage your tasks interactively")
            print("  /help                - Show this help message")
            print("  /exit or        - Exit the application")
            continue

        response = await runner.run_debug(f"User {user.first_name} ({user.email}) says: {user_input}", session_id=session_id)
        if session:
            session.state['user_id'] = user.id
            await session_service.update_session(session=session)

        texts = [r.output_text for r in response if hasattr(r, "output_text")]
        cli.print_output("\n".join(texts))

if __name__ == "__main__":
    asyncio.run(run_agent())

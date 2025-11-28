import asyncio
import uuid
from datetime import datetime, timedelta
from google.adk.runners import Runner
from database import init_db
import config
import agent_setup
import session_manager
import cli

# Setup environment
config.setup_environment()

# Initialize database
init_db()

# Setup Agent, Session Service, and Runner
root_agent = agent_setup.create_root_agent()
session_service = session_manager.create_session_service()
runner = Runner(agent=root_agent, session_service=session_service, app_name="task_management_system")
print("✅ Runner created.")

async def run_agent():
    """Main function to run the agent after authentication."""
    user = await cli.handle_authentication()
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

        response = await runner.run_debug(f"User {user.first_name} ({user.email}) says: {user_input}", session_id=session_id)
        if session:
            session.state['user_id'] = user.id
            await session_service.update_session(session=session)

        texts = [r.output_text for r in response if hasattr(r, "output_text")]
        cli.print_output("\n".join(texts))

if __name__ == "__main__":
    asyncio.run(run_agent())

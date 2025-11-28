from google.adk.sessions import DatabaseSessionService
from sqlalchemy import create_engine, text
import database

def create_session_service(db_url="sqlite:///task_management.db"):
    """Creates and returns the database session service."""
    session_service = DatabaseSessionService(db_url)
    print("✅ Database Session Service created.")
    return session_service

def get_last_session(user_id, db_url="sqlite:///task_management.db"):
    """Retrieves the most recent session for the given user."""
    engine = create_engine(db_url)
    with engine.connect() as connection:
        # Query for the latest session for this user
        result = connection.execute(
            text("SELECT id, update_time FROM sessions WHERE user_id = :user_id ORDER BY update_time DESC LIMIT 1"),
            {"user_id": user_id}
        ).fetchone()
        
        if result:
            return {"id": result[0], "update_time": result[1]}
    return None

def update_session_user_id(session_id, user_id, db_url="sqlite:///task_management.db"):
    """Updates the user_id for the given session."""
    engine = create_engine(db_url)
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(
                text("UPDATE sessions SET user_id = :user_id WHERE id = :session_id"),
                {"user_id": user_id, "session_id": session_id}
            )

from tools import auth
from database.models import User
from database.connection import SessionLocal

try:
    print("Attempting to authenticate...")
    user = auth.authenticate_user("test@example.com", "Password123")
    if user:
        print(f"Authentication successful: {user.email}")
    else:
        print("Authentication failed")
except Exception as e:
    print(f"Error during authentication: {e}")

from tools import auth
import uuid

email = f"test_{uuid.uuid4()}@example.com"
password = "Password123"

print(f"Creating user {email}...")
try:
    user = auth.create_user("Test", "User", email, password, "Dev", "Desc")
    print(f"User created: {user.id}")
    
    print("Authenticating...")
    auth_user = auth.authenticate_user(email, password)
    if auth_user:
        print("Authentication successful!")
    else:
        print("Authentication failed!")
except Exception as e:
    print(f"Error: {e}")

import requests

BASE_URL = "http://127.0.0.1:8000/api"
EMAIL = "final@example.com"
PASSWORD = "Password123"

session = requests.Session()

print("Logging in...")
try:
    resp = session.post(f"{BASE_URL}/login", json={"email": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        exit(1)
    print("Login successful.")

    print("Creating task...")
    resp = session.post(f"{BASE_URL}/tasks", json={"description": "Test task creation failure"})
    if resp.status_code != 200:
        print(f"Task creation failed: {resp.status_code} - {resp.text}")
    else:
        print(f"Task creation successful: {resp.json()}")
except Exception as e:
    print(f"An error occurred: {e}")

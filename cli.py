import sys
import auth

def get_user_input(prompt=None):
    """Reads input from stdin with an optional prompt."""
    if prompt:
        print(prompt, end='', flush=True)
    return sys.stdin.readline().strip()

def print_output(text):
    """Prints output to stdout."""
    print(text)

async def handle_authentication():
    """Handles the user authentication flow."""
    while True:
        has_account = get_user_input("Do you have an account? (yes/no): ").lower()
        
        if has_account == 'yes':
            try:
                email = get_user_input("Email: ")
                password = get_user_input("Password (visible): ")
                user = auth.authenticate_user(email, password)
                if user:
                    print_output(f"Welcome back, {user.first_name}!")
                    return user
                else:
                    print_output("Invalid credentials. Please try again.")
            except auth.RateLimitException as e:
                print_output(e)
        elif has_account == 'no':
            print_output("Let's create an account for you.")
            first_name = get_user_input("First Name: ")
            last_name = get_user_input("Last Name: ")
            email = get_user_input("Email: ")
            while True:
                try:
                    password = get_user_input("Password (visible): ")
                    password_confirm = get_user_input("Confirm Password (visible): ")
                    if password == password_confirm:
                        user = auth.create_user(first_name, last_name, email, password)
                        print_output(f"Account created successfully! Welcome, {user.first_name}!")
                        return user
                    else:
                        print_output("Passwords do not match. Please try again.")
                except ValueError as e:
                    print_output(e)
                    if "Email already registered" in str(e):
                        email = get_user_input("Email: ")
                    continue
        else:
            print_output("Invalid input. Please enter 'yes' or 'no'.")

def prompt_session_choice(last_session):
    """Prompts the user to resume the last session or start a new one."""
    print_output(f"\nWelcome back! You have a previous session from {last_session['update_time']}.")
    print_output("[1] Resume last session")
    print_output("[2] Start new session")
    
    while True:
        choice = get_user_input("Enter your choice (1 or 2): ")
        if choice == '1':
            return 'resume'
        elif choice == '2':
            return 'new'
        else:
            print_output("Invalid choice. Please enter 1 or 2.")

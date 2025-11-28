# Authentication System Guide

This guide provides an overview of the authentication and session management system for the AI Agentic Task Management System.

## How it Works

The authentication system is designed to protect all tools and agents from unauthorized access. It requires users to authenticate at the beginning of each interaction. The system supports both new user registration and login for existing users.

### Authentication Flow

1.  **Initial Prompt:** The user is asked if they have an account.
2.  **Existing User:** If the user has an account, they are prompted for their email and password. The system then validates their credentials.
3.  **New User:** If the user does not have an account, they are prompted to create one by providing their first name, last name, email, and a password.
4.  **Session Creation:** Upon successful authentication, a new session is created for the user. The session ID is used to track the user's interaction with the system.
5.  **Session Expiration:** Sessions expire after a configurable period of inactivity (default is 30 minutes).

## API and Functions

### `auth.py`

-   `get_password_hash(password)`: Hashes a plain-text password using bcrypt.
-   `verify_password(plain_password, hashed_password)`: Verifies a plain-text password against a hashed password.
-   `create_user(first_name, last_name, email, password)`: Creates a new user in the database.
-   `get_user_by_email(email)`: Retrieves a user from the database by their email address.
-   `authenticate_user(email, password)`: Authenticates a user by verifying their email and password.

### `sessions.py`

-   `create_session(user_id)`: Creates a new session for a user.
-   `get_session(session_id)`: Retrieves a session from the database by its ID.
-   `is_session_expired(session)`: Checks if a session has expired.
-   `delete_session(session_id)`: Deletes a session from the database.

## Usage Examples

To run the application, simply execute the `main.py` script:

```bash
python main.py
```

The application will guide you through the authentication process.

## Troubleshooting

-   **Invalid Credentials:** If you are unable to log in, please double-check your email and password. If you have forgotten your password, you will need to create a new account.
-   **Session Expired:** If your session expires, you will be prompted to log in again.
-   **Database Errors:** If you encounter any database errors, please ensure that the `task_management.db` file is not corrupted and that you have the necessary permissions to read and write to it.

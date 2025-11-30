# AI Task Manager

AI Task Manager is an intelligent, web-based task management system designed to streamline workflows for teams and small businesses. Powered by an AI agent, it transforms natural language descriptions into well-structured tasks, eliminating the friction of manual data entry and allowing your team to focus on what matters most.

## Key Features

- **AI-Powered Task Creation:** Simply describe a task in plain English, and our AI agent will intelligently extract the title, description, priority, and importance.
- **Intuitive Web Interface:** A clean, modern, and responsive web UI allows for seamless task management, from creation to completion.
- **User and Task Management:** The system supports user registration, login, and personalized task dashboards.
- **Task Filtering:** Easily filter tasks to see what's assigned to you or what you've assigned to others.
- **Status Updates:** Update task statuses with a single click to keep your team informed of your progress.

## Technology Stack

- **Backend:** Python, FastAPI, Google's Agent Development Kit (ADK), SQLAlchemy, SQLite
- **Frontend:** HTML, Tailwind CSS, Vanilla JavaScript
- **Authentication:** bcrypt for secure password hashing

## Setup and Installation

To get started with the AI Task Manager, follow these simple steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    -   Create a `.env` file in the root of the project by copying the `.env_example` file:
        ```bash
        cp .env_example .env
        ```
    -   Open the `.env` file and add your Google API key:
        ```
        GOOGLE_API_KEY="your-google-api-key"
        ```

4.  **Initialize the database:**
    ```bash
    python -c "from database import init_db; init_db()"
    ```

## How to Run

You can interact with the AI Task Manager through either the web interface or the command-line interface (CLI).

### Running the Web Server

To start the web server and use the application through your browser, run the following command:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

You can then access the application at `http://127.0.0.1:8000`.

### Running the Command-Line Interface (CLI)

To use the CLI, run the `cli.py` script:

```bash
python cli.py
```

The CLI will guide you through the available commands for user and task management.

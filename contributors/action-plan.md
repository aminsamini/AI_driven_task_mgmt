# Action Plan for Local Development

This document outlines the steps to set up the local development environment for the AI Agentic Task Management System. It provides a step-by-step guide to building and running your first AI agent using the Agent Development Kit (ADK).

## 1. Setup

### 1.1. Install Dependencies

First, you need to install the necessary Python packages. Run the following command in your terminal:

```bash
pip install -r requirements.txt
```

This will install the `google-adk` and other required libraries.

### 1.2. Set Environment Variables

You will need to configure your environment variables. Create a `.env` file in the root of the project and add the following:

```
# .env file
GOOGLE_API_KEY="YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your Google credentials.

Then, in your Python code, load the environment variable and set up the API key:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("🚫 GOOGLE_API_KEY not found in .env file!")

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

print("✅ Gemini API key setup complete.")
```

## 2. Building Your First AI Agent

### 2.1. Import ADK Components

Import the specific components you'll need from the Agent Development Kit and the Generative AI library.

```python
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

print("✅ ADK components imported successfully.")
```

### 2.2. Configure Retry Options (Optional but Recommended)

When working with LLMs, you may encounter transient errors like rate limits or temporary service unavailability. Retry options automatically handle these failures by retrying the request with exponential backoff.

```python
retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)
```

### 2.3. Define an Agent

-   **name and description:** A simple name and description to identify our agent.
-   **model:** The specific LLM that will power the agent's reasoning. We'll use "gemini-1.5-flash".
-   **instruction:** The agent's guiding prompt. This tells the agent what its goal is and how to behave.
-   **tools:** A list of tools that the agent can use. To start, we'll give it the `google_search` tool, which lets it find up-to-date information online.

```python
root_agent = Agent(
    name="helpful_assistant",
    model=Gemini(
        model="gemini-1.5-flash",
        retry_options=retry_config
    ),
    description="A simple agent that can answer general questions.",
    instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
    tools=[google_search],
)

print("✅ Root Agent defined.")
```

### 2.4. Run Your Agent

To do this, you need a Runner, which is the central component within ADK that acts as the orchestrator. It manages the conversation, sends our messages to the agent, and handles its responses.

#### A. Create an InMemoryRunner and tell it to use our `root_agent`:

```python
import asyncio

async def main():
    runner = InMemoryRunner(agent=root_agent)
    print("✅ Runner created.")
    response = await runner.run_debug(
        "What is Agent Development Kit from Google? What languages is the SDK available in?"
    )
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

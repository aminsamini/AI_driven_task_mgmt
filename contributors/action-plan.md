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

## 3. Agent Architectures: From a Single Agent to Multi-Agent Systems

While a single, powerful agent can handle many tasks, complex problems often benefit from a multi-agent approach. This involves creating a team of specialized AI agents that collaborate to achieve a goal. This section explores different workflow patterns for orchestrating these agents.

### 3.1. Sequential Workflows

In a sequential workflow, agents work in an assembly line, with the output of one agent becoming the input for the next. This is useful for tasks that have a clear, linear progression of steps.

**Example: Research and Summarize**

Let's create two agents: one to research a topic and another to summarize the findings.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import SequentialRunner
from google.adk.tools import google_search

# Define the Researcher Agent
researcher = Agent(
    name="researcher",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a researcher. Your job is to find information on a given topic.",
    tools=[google_search],
)

# Define the Summarizer Agent
summarizer = Agent(
    name="summarizer",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a summarizer. Your job is to take the given text and summarize it concisely.",
)

async def run_sequential_workflow():
    # Create a SequentialRunner with the two agents
    runner = SequentialRunner(agents=[researcher, summarizer])
    print("✅ Sequential Runner created.")

    # Run the workflow
    response = await runner.run_debug("What are the latest advancements in AI?")
    print(response)

if __name__ == "__main__":
    asyncio.run(run_sequential_workflow())
```

### 3.2. Parallel Workflows

In a parallel workflow, multiple agents work independently on different parts of a task, and their results are combined at the end. This is ideal for tasks that can be broken down into independent sub-tasks.

**Example: Multi-faceted Research**

Imagine you need to research a company from different perspectives (e.g., financial, technical, and market).

```python
import asyncio
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import ParallelRunner
from google.adk.tools import google_search

# Define agents for different research perspectives
financial_analyst = Agent(
    name="financial_analyst",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="Analyze the financial health of a company.",
    tools=[google_search]
)

technical_analyst = Agent(
    name="technical_analyst",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="Analyze the technology stack of a company.",
    tools=[google_search]
)

market_analyst = Agent(
    name="market_analyst",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="Analyze the market position of a company.",
    tools=[google_search]
)

async def run_parallel_workflow():
    # Create a ParallelRunner with the analyst agents
    runner = ParallelRunner(agents=[financial_analyst, technical_analyst, market_analyst])
    print("✅ Parallel Runner created.")

    # Run the workflow
    response = await runner.run_debug("Analyze Google.")
    print(response)

if __name__ == "__main__":
    asyncio.run(run_parallel_workflow())
```

### 3.3. Loop Workflows

Loop workflows allow for iterative processes where an agent's output can be fed back to itself or another agent for refinement. This is useful for tasks that require continuous improvement or feedback cycles.

**Example: Iterative Content Creation**

Let's create a writer agent that generates text and then refines it based on feedback.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import LoopingRunner

# Define the Writer Agent
writer = Agent(
    name="writer",
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a writer. Generate a short story based on the given prompt. Then, refine it based on the feedback provided.",
)

async def run_loop_workflow():
    # Create a LoopingRunner
    runner = LoopingRunner(agent=writer, num_loops=3) # Loop 3 times for refinement
    print("✅ Looping Runner created.")

    # Run the workflow
    response = await runner.run_debug("Write a story about a robot who discovers music.")
    print(response)

if __name__ == "__main__":
    asyncio.run(run_loop_workflow())
```
## 4. Custom Agent Tools

While pre-built tools like `google_search` are powerful, you can extend your agent's capabilities by creating custom tools. These are essentially Python functions that your agent can learn to use.

### 4.1. Why Do Agents Need Tools?

LLMs are trained on vast amounts of text data, but their knowledge is static and they lack real-world interaction capabilities. Tools bridge this gap by allowing agents to:

-   **Access Up-to-Date Information:** Connect to APIs, databases, or the web for the latest information.
-   **Perform Complex Calculations:** Use libraries like NumPy or specialized financial modeling tools.
-   **Interact with Systems:** Control software, send emails, or manage smart devices.

### 4.2. Creating a Simple Calculator Tool

Let's create a tool that can perform basic arithmetic operations. The `@tool` decorator from the ADK makes it easy to turn a Python function into a tool that an agent can use.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.core import astream_generator, astream_content
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool import tool

@tool
def calculator(operation: str, a: int, b: int) -> int:
    """
    A simple calculator that can perform addition, subtraction, multiplication, and division.
    Args:
        operation: The operation to perform ('add', 'subtract', 'multiply', 'divide').
        a: The first number.
        b: The second number.
    Returns:
        The result of the operation.
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return a / b
    else:
        raise ValueError("Invalid operation. Please use 'add', 'subtract', 'multiply', or 'divide'.")

async def run_with_custom_tool():
    agent_with_calculator = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a helpful assistant with a calculator.",
        tools=[calculator]
    )

    prompt = "What is 2 + 2?"
    print(f"Running agent with prompt: {prompt}")
    async for event in astream_generator(agent_with_calculator.run(prompt)):
        astream_content(event)

if __name__ == "__main__":
    asyncio.run(run_with_custom_tool())
```

## 5. Advanced Tool Patterns and Best Practices

This section covers advanced techniques for building more robust, interactive, and intelligent agent tools.

### 5.1. Model Context Protocol: Providing Temporary Context

Sometimes, you need to give an agent temporary information that is relevant only for the current session (e.g., user preferences, temporary files). The Model Context Protocol allows you to inject this data into the model's context without permanently altering the agent's instructions.

**Example: A "Talk Like a Pirate" Agent**

Here's how to temporarily instruct an agent to respond like a pirate using `model_context`.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.core import astream_generator, astream_content
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool import tool

async def run_with_model_context():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a helpful assistant."
    )

    prompt = "Tell me a joke."
    model_context = "Talk like a pirate."

    print(f"Running agent with prompt: '{prompt}' and context: '{model_context}'")
    async for event in astream_generator(agent.run(prompt, model_context=model_context)):
        astream_content(event)

if __name__ == "__main__":
    asyncio.run(run_with_model_context())
```

### 5.2. Long-Running Operations & Human-in-the-Loop

Some tools perform tasks that take a long time or require external validation (e.g., waiting for human approval, running a lengthy computation). Standard tool calls are synchronous and will time out if the task takes too long.

The **Human-in-the-Loop** pattern solves this by splitting the operation into two parts:
1.  **Initiation**: The tool starts the long-running task and immediately returns a `PENDING` status with a unique `operation_id`.
2.  **Completion**: A separate `human_approval` tool is called with the `operation_id` to signal that the task is complete and return the final result.

**Example: A Tool Requiring User Approval**

Let's build a tool that simulates an action requiring user confirmation.

```python
import asyncio
from google.adk.agents import Agent
from google.adk.core import astream_generator, astream_content
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool import tool, Tool, tool_from_function
from google.adk.tools.human_tools import human_approval

# In-memory store for pending operations
_PENDING_OPERATIONS = {}

@tool
def my_long_running_task() -> dict:
    """Starts a long-running task that requires human approval."""
    operation_id = f"op_{len(_PENDING_OPERATIONS) + 1}"
    _PENDING_OPERATIONS[operation_id] = "My important data"
    return {"status": "PENDING", "operation_id": operation_id}

# The agent needs both the initiating tool and the approval tool
tools = [my_long_running_task, human_approval]

async def run_human_in_the_loop():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        tools=tools,
        instruction=(
            "You have a tool that may require human approval. "
            "If the tool returns a PENDING status, stop and wait for the user. "
            "Do not call the human_approval tool yourself."
        )
    )

    prompt = "Run my long running task."
    print(f"Running agent with prompt: '{prompt}'")

    # This will store the pending operation ID
    operation_id = None

    async for event in astream_generator(agent.run(prompt)):
        if event.type == "tool_code" and event.data.name == "my_long_running_task":
            print("⏳ Agent is about to run the long-running task...")
        elif event.type == "tool_output" and event.data.name == "my_long_running_task":
            # Capture the operation_id from the tool's output
            if event.data.output.get("status") == "PENDING":
                operation_id = event.data.output.get("operation_id")
                print(f"🚦 Task is pending with ID: {operation_id}. Waiting for approval.")
        else:
            astream_content(event)

    # Simulate waiting for human approval and then completing the task
    if operation_id:
        print("\n✅ Simulating human approval...\n")
        final_prompt = f"The user has approved operation {operation_id}. What is the result?"

        async for event in astream_generator(agent.run(final_prompt)):
            if event.type == "tool_code" and event.data.name == "human_approval":
                # Actually retrieve the data now that the operation is "approved"
                event.data.kwargs["result"] = _PENDING_OPERATIONS.pop(operation_id, "Data not found.")
            astream_content(event)

if __name__ == "__main__":
    asyncio.run(run_human_in_the_loop())
```

## 6. Managing Agent Memory and State with Sessions

By default, agents are stateless. Each time you call the `.run()` method, it's treated as a new, independent conversation. To build a true conversational agent that remembers past interactions, you need to manage its session and memory.

### 6.1. In-Memory Sessions

The simplest way to give your agent memory is to use an `InMemorySessionService`. This service stores the conversation history in memory, allowing the agent to "remember" previous turns within the same session.

**Example: A Simple Chatbot**

```python
import asyncio
import uuid
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

async def run_in_memory_session():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a helpful chatbot. Keep your responses brief."
    )

    # Create an in-memory session service
    session_service = InMemorySessionService()
    runner = InMemoryRunner(agent=agent, session_service=session_service)

    # Generate a unique ID for this conversation
    session_id = str(uuid.uuid4())
    print(f"Starting session: {session_id}\n")

    # First turn
    response1 = await runner.run_debug("My name is Alex.", session_id=session_id)
    print(f"User: My name is Alex.\nAgent: {response1['output']}\n")

    # Second turn
    response2 = await runner.run_debug("What is my name?", session_id=session_id)
    print(f"User: What is my name?\nAgent: {response2['output']}")

if __name__ == "__main__":
    asyncio.run(run_in_memory_session())
```

### 6.2. Persistent Sessions with a Database

For applications that need to remember conversations across restarts, you can use a `DatabaseSessionService`. This service connects to a database (like SQLite) to store the session history permanently.

```python
import asyncio
import uuid
import sqlalchemy
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.sessions import DatabaseSessionService

async def run_persistent_session():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a helpful chatbot."
    )

    # Set up the database engine (using a file-based SQLite DB for persistence)
    engine = sqlalchemy.create_engine("sqlite:///task_management.db")
    session_service = DatabaseSessionService.create_tables_from_engine(engine)
    runner = InMemoryRunner(agent=agent, session_service=session_service)

    session_id = str(uuid.uuid4())
    print(f"Starting persistent session: {session_id}\n")

    await runner.run_debug("Remember this color: blue.", session_id=session_id)

    # In a real app, you could now restart and still access the session.
    # Here, we'll just create a new runner to simulate reconnecting.
    print("Reconnecting to session...")
    runner2 = InMemoryRunner(agent=agent, session_service=session_service)
    response = await runner2.run_debug("What color did I ask you to remember?", session_id=session_id)
    print(f"Agent response: {response['output']}")

if __name__ == "__main__":
    asyncio.run(run_persistent_session())
```

### 6.3. Context Compaction for Long Conversations

LLMs have a limited context window. As a conversation gets longer, you risk exceeding this limit. **Context compaction** is a feature that automatically summarizes the beginning of a conversation to save space while preserving key information.

```python
import asyncio
import uuid
from google.adk.agents import Agent, CompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.services.sessions import InMemorySessionService

async def run_with_compaction():
    summarizer_agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a summarizer. Briefly summarize the given text."
    )

    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        instruction="You are a helpful chatbot."
    )

    # Configure compaction to trigger when the context reaches 40 tokens
    compaction_config = CompactionConfig(
        compactor=summarizer_agent,
        compact_every_n_storage_turns=2,
    )

    session_service = InMemorySessionService(compaction_config=compaction_config)
    runner = InMemoryRunner(agent=agent, session_service=session_service)
    session_id = str(uuid.uuid4())

    print("Running conversation with context compaction enabled...")
    # These turns will fill up the context and trigger compaction
    await runner.run_debug("My favorite animal is a dog.", session_id=session_id)
    await runner.run_debug("My favorite color is red.", session_id=session_id)
    response = await runner.run_debug("What is my favorite animal?", session_id=session_id)
    print(f"Agent response: {response['output']}")

if __name__ == "__main__":
    asyncio.run(run_with_compaction())
```

### 6.4. Using Session State

You can store and retrieve arbitrary data within a session's state. This is useful for tracking information that isn't part of the dialogue but is relevant to the task.

```python
import asyncio
import uuid
from google.adk.agents import Agent
from google.adk.core.events import InferenceEvent, FinishEvent
from google.adk.core.inference import Answer, Code, Observation
from google.adk.core.session import Session
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.services.sessions import InMemorySessionService
from google.adk.tools.tool import tool

@tool
def update_and_get_counter(session: Session, increment: int = 1):
    """Increments and returns a counter stored in the session state."""
    counter = session.state.get("counter", 0)
    counter += increment
    session.state["counter"] = counter
    return {"counter": counter}

async def run_with_session_state():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        tools=[update_and_get_counter]
    )
    runner = InMemoryRunner(agent=agent, session_service=InMemorySessionService())
    session_id = str(uuid.uuid4())

    # Run the tool multiple times to see the state persist
    await runner.run_debug("Increment the counter.", session_id=session_id)
    response = await runner.run_debug("Increment it again by 2.", session_id=session_id)
    print(f"Final counter value: {response['output']}")

if __name__ == "__main__":
    asyncio.run(run_with_session_state())
```

## 7. Empowering Agents with Long-Term Memory (RAG)

While sessions provide short-term memory for an agent within a single conversation, true intelligence requires the ability to learn from and recall information across multiple interactions. The ADK facilitates this through a `MemoryService` that implements Retrieval-Augmented Generation (RAG), allowing your agent to query a knowledge base built from past conversations.

**Key Concepts:**

*   **`VectorStore`**: A database that stores information as numerical vectors, enabling efficient similarity searches.
*   **`MemoryService`**: Manages the storage and retrieval of information from the `VectorStore`.
*   **Ingestion**: The process of adding new information (like a completed agent session) into the memory.
*   **Retrieval**: The process of searching the memory for information relevant to the current query.

### 7.1. Initialize a Vector Store and Memory Service

First, set up a vector store. The ADK supports various backends; here, we'll use an in-memory `Chroma` database. Then, create the `MemoryService` instance using this store.

```python
from google_adk.memory import ChromaVectorStore, MemoryService

# Set up an in-memory vector store
vector_store = ChromaVectorStore(
    collection_name="agent_memory_example"
)

# Initialize the MemoryService
memory_service = MemoryService(vector_store=vector_store)
```
> **Note**: For production systems, you would replace `ChromaVectorStore` with a persistent database solution.

### 7.2. Ingesting Session Data into Memory

To build your agent's knowledge base, you need to ingest data. You can manually add the history of a completed session to the `MemoryService`.

```python
from google_adk.memory import Session, MemoryService
from google_adk.agents import Agent
import uuid

# Assume 'agent' and 'memory_service' are already initialized
# Create a new session
session_id = str(uuid.uuid4())
session = Session(session_id=session_id)

# Simulate a conversation
agent.run(session=session, user_input="My name is Alex.")
agent.run(session=session, user_input="What is my name?") # Agent will respond with "Alex"

# Ingest the entire session history into the memory service
memory_service.ingest(session)
print("Session history has been saved to long-term memory.")
```

### 7.3. Enabling Memory Retrieval in Your Agent

To allow an agent to use the `MemoryService`, attach it using the `.set_memory()` method. The agent will then automatically query this memory when responding to user input.

```python
from google_adk.agents import Agent
from google_adk.memory import Session
import uuid

# Assume 'memory_service' is initialized and has ingested data
# Create a new agent and a new session
retrieval_agent = Agent(
    instructions="You are a helpful assistant."
)
retrieval_agent.set_memory(memory_service)

retrieval_session = Session(session_id=str(uuid.uuid4()))

# The agent can now recall information from the previous session
response = retrieval_agent.run(
    session=retrieval_session,
    user_input="Do you remember my name?"
)
print(response.output)
# Expected output: "Yes, your name is Alex."
```

### 7.4. Automating Memory Storage with Hooks

Manually ingesting every session is impractical. You can automate this process by attaching a `done_hook` to the session, which triggers when the session ends.

```python
from google_adk.agents import Agent
from google_adk.memory import Session
import uuid

# Assume 'memory_service' is initialized
# Define a hook that ingests the session into memory
def save_to_memory(session: Session) -> None:
    print(f"Saving session {session.session_id} to memory...")
    memory_service.ingest(session)
    print("Done!")

# Create a session with the hook
automated_session = Session(
    session_id=str(uuid.uuid4()),
    done_hook=save_to_memory
)

# Create an agent and run the session
hook_agent = Agent(instructions="You are a bot that remembers things.")
hook_agent.run(automated_session, "My favorite color is blue.")

# End the session to trigger the hook
automated_session.done()
```

### 7.5. Memory Consolidation

Over time, the memory store can become large and contain redundant information. **Memory consolidation** is the process of periodically summarizing related memories into a more concise format. The `MemoryService` provides a `.consolidate()` method for this purpose, which helps maintain the relevance and efficiency of your agent's knowledge base.

## 8. Agent Observability: Logs, Traces & Metrics

Observability is crucial for understanding, debugging, and improving your AI agents. It provides insights into an agent's internal reasoning, decision-making processes, and overall performance. The ADK offers several tools for this, including a web-based debugging UI and structured logging.

### 8.1. Debugging with the ADK Web UI

The ADK Web UI provides a visual interface to inspect the inner workings of your agent as it processes a request. You can see the prompts sent to the LLM, the tools it decides to use, and the final output.

**How to Launch the Web UI:**

1.  **Start the Server**: Run your agent script with `adk-run`. This command starts a web server that hosts the UI.

    ```bash
    adk-run your_agent_script.py
    ```

2.  **Access the UI**: Open your web browser and navigate to the URL provided in the terminal (usually `http://127.0.0.1:8080`).

**Example: Running an Agent with the Debugger**

Let's create a simple agent and run it with the ADK Web UI.

```python
# Save this as your_agent_script.py
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# Define an agent
my_agent = Agent(
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a helpful assistant.",
    tools=[google_search]
)

# The adk-run command will automatically serve this agent.
```

After running `adk-run your_agent_script.py`, you can go to the web UI, enter a prompt like "What's the weather in London?", and watch how the agent uses the `google_search` tool to find the answer.

### 8.2. Structured Logging for Production

While the Web UI is great for development, you'll need a more robust solution for production environments. The ADK's `astream_generator` provides a stream of events that you can log to capture the agent's activity.

You can create a custom `InferenceLogger` to process and store these events in a structured format (e.g., JSON).

```python
import asyncio
import json
from google.adk.agents import Agent
from google.adk.core import astream_generator
from google.adk.core.events import InferenceEvent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search

# A custom logger to handle inference events
class InferenceLogger:
    def __init__(self, log_file="inference_log.jsonl"):
        self._log_file = log_file

    async def log_event(self, event: InferenceEvent) -> None:
        with open(self._log_file, "a") as f:
            log_entry = {
                "timestamp": event.timestamp,
                "type": event.type,
                "data": str(event.data),
            }
            f.write(json.dumps(log_entry) + "\n")

async def run_with_logging():
    agent = Agent(
        model=Gemini(model="gemini-1.5-flash"),
        tools=[google_search],
        instruction="You are a helpful assistant."
    )
    logger = InferenceLogger()

    prompt = "What is the capital of France?"
    print(f"Running agent with logging for prompt: '{prompt}'")
    async for event in astream_generator(agent.run(prompt)):
        await logger.log_event(event)

    print(f"✅ Agent run complete. Logs saved to inference_log.jsonl")

if __name__ == "__main__":
    asyncio.run(run_with_logging())
```

This script will produce a `inference_log.jsonl` file with a detailed, structured log of the agent's execution, which can be invaluable for production monitoring and debugging.

### Evaluating Agent Performance

Evaluating your agent's performance is crucial to ensure it behaves as expected and meets quality standards. Evaluation can be done interactively for debugging or systematically for regression testing.

#### Interactive Evaluation with ADK Web UI

The ADK Web UI is an excellent tool for real-time, interactive evaluation. You can start the UI and test your agent with various inputs to observe its behavior instantly.

1.  **Start the ADK Web UI**:
    ```bash
    adk serve
    ```
2.  **Interact with Your Agent**: Open the web interface and send prompts to your agent. You can inspect the agent's responses, tool calls, and intermediate steps to debug and validate its logic.

#### Systematic Evaluation

For automated and consistent testing, create a suite of test cases. Each test case consists of an input prompt and an expected outcome.

1.  **Define a Test Dataset**: Create a list of prompts that cover various scenarios your agent should handle.

    ```python
    test_cases = [
        {"prompt": "Turn on the living room lights."},
        {"prompt": "Set the bedroom temperature to 72 degrees."},
        {"prompt": "Invalid command."},
    ]
    ```

2.  **Run the Evaluation**: Iterate through the test cases, run your agent, and compare the output to the expected results.

    ```python
    from adk.agent import Agent
    from adk.config import Config

    # Assume 'HomeAutomationAgent' is your defined agent
    agent = Agent(config=Config())

    def run_evaluation(agent, test_cases):
        results = []
        for case in test_cases:
            prompt = case["prompt"]
            response = agent.run(prompt)
            results.append({
                "prompt": prompt,
                "response": response,
            })
        return results

    # evaluation_results = run_evaluation(HomeAutomationAgent, test_cases)
    # print(evaluation_results)

    # Note: To run this, you would need to have the HomeAutomationAgent class defined
    # with its tools (e.g., set_temperature, control_lights). The example above
    # illustrates the structure of a systematic evaluation script.
    ```

#### User Simulation (Advanced)

For more complex scenarios, you can simulate user interactions using another agent. This allows you to test multi-turn conversations and more dynamic behaviors. This is an advanced topic covered in later sections.

## 9. Agent-to-Agent (A2A) Communication

Agent-to-Agent (A2A) communication allows you to build sophisticated systems where multiple specialized agents collaborate. One agent can expose its capabilities as a tool that other agents can use. This is achieved by running an agent as a server and creating a client tool that connects to it.

### 9.1. Create the "Exposed" Agent

First, define the agent that will be providing the service. This agent has its own set of tools and instructions.

```python
# Save as product_catalog_agent.py
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool import tool

@tool
def get_product_info(product_name: str) -> dict:
    """Looks up product information in a catalog."""
    # In a real app, this would query a database.
    products = {"ADK T-shirt": {"price": 25, "in_stock": True}}
    return products.get(product_name, {"error": "Product not found"})

product_catalog_agent = Agent(
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a helpful product catalog assistant.",
    tools=[get_product_info]
)
```

### 9.2. Expose the Agent as a Tool

Use the `A2A` class to wrap your agent and expose it as a tool that other agents can use.

```python
# Save as product_catalog_server.py
from google.adk.a2a import A2A
from product_catalog_agent import product_catalog_agent

# Expose the agent via A2A
a2a_tool = A2A(
    name="product_catalog",
    description="Tool for querying the product catalog.",
    agent=product_catalog_agent,
    host="127.0.0.1",
    port=50051,
)
```

### 9.3. Start the Agent Server

Run the agent as a server using `adk-run`.

```bash
adk-run product_catalog_server.py
```
Your product catalog agent is now running and can be called by other agents.

### 9.4. Create the "Consumer" Agent

Now, create the agent that will use the `product_catalog` tool.

```python
# Save as customer_support_agent.py
import asyncio
from google.adk.agents import Agent
from google.adk.core import astream_generator, astream_content
from google.adk.models.google_llm import Gemini
from google.adk.a2a.client import client_from_a2a_tool
from product_catalog_server import a2a_tool # Import from your server file

# Create a client tool that connects to the server
product_catalog_tool = client_from_a2a_tool(a2a_tool)

# Create the customer support agent
customer_support_agent = Agent(
    model=Gemini(model="gemini-1.5-flash"),
    instruction="You are a customer support agent. Use the product catalog to answer questions.",
    tools=[product_catalog_tool],
)

async def main():
    prompt = "What is the price of the ADK T-shirt?"
    async for event in astream_generator(customer_support_agent.run(prompt)):
        astream_content(event)

if __name__ == "__main__":
    asyncio.run(main())
```

### 9.5. Test the A2A Communication

1.  Make sure the product catalog server is running.
2.  Run the customer support agent script:

    ```bash
    python customer_support_agent.py
    ```

The customer support agent will call the product catalog agent to get the price of the T-shirt and provide the answer. This demonstrates a complete A2A workflow.

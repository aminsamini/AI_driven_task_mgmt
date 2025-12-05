import asyncio
from unittest.mock import MagicMock, AsyncMock
from google.genai.errors import ServerError
from agents.task_agents import TaskCreationWorkflow
import time

async def test_retry_logic():
    print("Starting retry logic test...")
    
    # Mock the runner and its run_debug method
    mock_runner = MagicMock()
    
    # Create a side effect that raises ServerError 2 times then succeeds
    # We need to simulate the response object expected by extract_text
    mock_response_event = MagicMock()
    mock_response_event.output_text = "2025-12-31 17:00:00"
    
    # We need an async iterator for run_debug return value
    async def async_response_gen():
        yield mock_response_event

    # We need to simulate the failure. 
    # Since _run_agent calls await runner.run_debug(prompt), we need to mock run_debug.
    # However, run_debug returns an async generator usually, but here we are mocking it.
    # Let's look at how _run_agent is implemented:
    # return await runner.run_debug(prompt)
    
    # So run_debug should be an async function that returns something.
    # But wait, in the original code:
    # deadline_resp = await deadline_runner.run_debug(...)
    # deadline_str = extract_text(deadline_resp)
    # extract_text iterates over response.
    
    # So run_debug returns an iterable (async or sync? likely async generator or just an iterable).
    # In the stack trace: "async for event in self.run_async(" ...
    # So run_debug returns an async generator.
    
    # But for our test, we are mocking _run_agent's internal call to runner.run_debug.
    
    workflow = TaskCreationWorkflow(user_id=1)
    
    # We will mock the _run_agent method to test the retry decorator? 
    # No, we want to test that _run_agent *has* the retry decorator working.
    # So we should call _run_agent with a mock runner that fails.
    
    fail_count = 0
    
    async def mock_run_debug(*args, **kwargs):
        nonlocal fail_count
        fail_count += 1
        print(f"Attempt {fail_count}...")
        if fail_count < 3:
            print("Simulating 503 Error")
            # Create a fake response object to pass to ServerError
            fake_response = MagicMock()
            # The second argument to ServerError seems to be response_json (dict), not message (str)
            error_json = {'error': {'code': 503, 'message': 'The model is overloaded. Please try again later.', 'status': 'UNAVAILABLE'}}
            raise ServerError(503, error_json, fake_response)
        print("Simulating Success")
        return [mock_response_event] # Return a list which is iterable

    mock_runner.run_debug = mock_run_debug
    
    start_time = time.time()
    try:
        # We call _run_agent directly to test it
        result = await workflow._run_agent(mock_runner, "test prompt")
        end_time = time.time()
        
        print(f"Test passed! Result obtained after {fail_count} attempts.")
        print(f"Time taken: {end_time - start_time:.2f}s (should be > 0 due to backoff)")
        
        if fail_count == 3:
            print("SUCCESS: Retry mechanism worked as expected (retried twice).")
        else:
            print(f"FAILURE: Expected 3 attempts, got {fail_count}.")
            
    except Exception as e:
        print(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_retry_logic())

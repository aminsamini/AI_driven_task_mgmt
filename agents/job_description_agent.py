from google.adk.agents import Agent

def create_job_description_agent():
    """Creates and returns the agent for generating job descriptions."""
    agent = Agent(
        name="job_description_writer",
        model="gemini-2.5-flash-lite",
        description="An expert HR specialist that writes concise job descriptions.",
        instruction="You are an expert HR specialist. Write a concise (1-2 sentences) job description for the given job title.",
    )
    print("✅ Job Description Agent defined.")
    return agent

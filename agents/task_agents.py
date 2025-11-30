from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from tools.task_tools import get_all_candidates, save_task_to_db
from datetime import datetime
import json
import asyncio

# 1. Deadline Agent
deadline_agent = Agent(
    name="deadline_agent",
    model="gemini-2.5-flash-lite",
    description="Predicts deadlines for tasks.",
    instruction="""You are an expert project manager. 
    Analyze the task description and predict a reasonable deadline. 
    Return ONLY the deadline in 'YYYY-MM-DD HH:MM:SS' format. 
    If no specific time is implied, assume 5:00 PM on the calculated date.
    If the description is vague, assume 24 hours from now.
    Current time is provided in the prompt."""
)

# 2. Assignee Agent
assignee_agent = Agent(
    name="assignee_agent",
    model="gemini-2.5-flash-lite",
    description="Finds the best assignee for a task.",
    instruction="""You are an HR specialist. 
    You will be given a task description and a list of candidates with their job positions and descriptions.
    Select the best candidate for the task.
    Return ONLY the ID of the selected candidate.
    If no suitable candidate is found, return 'None'."""
)

# 3. Details Agent
details_agent = Agent(
    name="details_agent",
    model="gemini-2.5-flash-lite",
    description="Generates task titles and refined descriptions.",
    instruction="""You are a technical writer.
    Create a concise, action-oriented title and a clear, detailed description for the task.
    Return your response in JSON format:
    {
        "title": "The Title",
        "description": "The detailed description"
    }"""
)

# 4. Priority Agent
priority_agent = Agent(
    name="priority_agent",
    model="gemini-2.5-flash-lite",
    description="Determines task importance and priority.",
    instruction="""You are a strategic planner.
    Assess the task's importance and priority based on the description.
    Rate both on a scale of 1 to 5 (5 being highest).
    Return your response in JSON format:
    {
        "importance": "3",
        "priority": "4"
    }"""
)

# 5. Suggestion Agent
suggestion_agent = Agent(
    name="suggestion_agent",
    model="gemini-2.5-flash-lite",
    description="Provides suggestions for the assignee.",
    instruction="""You are a senior mentor.
    Provide helpful suggestions, resources, or starting points for the person who will do this task.
    Keep it brief and actionable."""
)


def extract_text(response):
    texts = []
    for event in response:
        if hasattr(event, 'output_text'):
             texts.append(event.output_text)
        elif hasattr(event, 'content') and event.content and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    texts.append(part.text)
    return "\n".join(texts).strip()

class TaskCreationWorkflow:
    def __init__(self, user_id):
        self.user_id = user_id
        self.session_service = InMemorySessionService()
        
    async def run(self, user_input):
        # 1. Predict Deadline
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        deadline_runner = Runner(agent=deadline_agent, session_service=self.session_service, app_name="task_gen")
        deadline_resp = await deadline_runner.run_debug(f"Task: {user_input}. Current time: {current_time}")
        deadline_str = extract_text(deadline_resp)
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            # Fallback if format is wrong
            deadline = datetime.now()
            print(f"Warning: Could not parse deadline '{deadline_str}', using now.")

        # 2. Find Assignee
        candidates = get_all_candidates()
        candidates_str = json.dumps(candidates, indent=2)
        assignee_runner = Runner(agent=assignee_agent, session_service=self.session_service, app_name="task_gen")
        assignee_resp = await assignee_runner.run_debug(f"Task: {user_input}\nCandidates:\n{candidates_str}")
        assignee_id = extract_text(assignee_resp)
        
        if assignee_id == 'None' or not any(c['id'] == assignee_id for c in candidates):
             # Fallback to creator if no match
             assignee_id = self.user_id
             print("Warning: No suitable assignee found, assigning to creator.")

        # 3. Generate Details
        details_runner = Runner(agent=details_agent, session_service=self.session_service, app_name="task_gen")
        details_resp = await details_runner.run_debug(f"Task: {user_input}")
        details_text = extract_text(details_resp)
        try:
            details_json = json.loads(details_text.replace('```json', '').replace('```', ''))
            title = details_json.get("title", "New Task")
            description = details_json.get("description", user_input)
        except json.JSONDecodeError:
            title = "New Task"
            description = user_input
            print("Warning: Could not parse details JSON.")

        # 4. Predict Priority
        priority_runner = Runner(agent=priority_agent, session_service=self.session_service, app_name="task_gen")
        priority_resp = await priority_runner.run_debug(f"Task: {user_input}")
        priority_text = extract_text(priority_resp)
        try:
            priority_json = json.loads(priority_text.replace('```json', '').replace('```', ''))
            importance = priority_json.get("importance", "3")
            priority = priority_json.get("priority", "3")
        except json.JSONDecodeError:
            importance = "3"
            priority = "3"
            print("Warning: Could not parse priority JSON.")

        # 5. Make Suggestions
        suggestion_runner = Runner(agent=suggestion_agent, session_service=self.session_service, app_name="task_gen")
        suggestion_resp = await suggestion_runner.run_debug(f"Task: {user_input}")
        suggestions = extract_text(suggestion_resp)

        # 6. Save to DB
        result_msg = save_task_to_db(
            title=title,
            description=description,
            assign_by=self.user_id,
            assignee_id=assignee_id,
            importance=importance,
            priority=priority,
            deadline=deadline,
            suggestions=suggestions
        )
        
        # Find assignee name
        assignee_name = "Unknown"
        for c in candidates:
            if c['id'] == assignee_id:
                assignee_name = c['name']
                break
        if assignee_name == "Unknown" and assignee_id == self.user_id:
             assignee_name = "You"

        return {
            "status": "success",
            "message": result_msg,
            "assignee_name": assignee_name,
            "task_title": title
        }
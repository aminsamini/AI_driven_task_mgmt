from database.connection import SessionLocal
from database.models import User, Task
from datetime import datetime

def get_all_candidates():
    """
    Retrieves all users from the database who can be potential assignees.
    Returns a list of dictionaries containing user ID, name, position, and job description.
    """
    session = SessionLocal()
    try:
        users = session.query(User).all()
        candidates = []
        for user in users:
            candidates.append({
                "id": user.id,
                "name": f"{user.first_name} {user.last_name}",
                "position": user.position,
                "job_description": user.job_description
            })
        return candidates
    except Exception as e:
        print(f"Error fetching candidates: {e}")
        return []
    finally:
        session.close()

def save_task_to_db(title, description, assign_by, assignee_id, importance, priority, deadline, suggestions):
    """
    Saves a new task to the database.
    
    Args:
        title (str): The title of the task.
        description (str): The description of the task.
        assign_by (str): The ID of the user creating the task.
        assignee_id (str): The ID of the user assigned to the task.
        importance (str): Importance level (1-5).
        priority (str): Priority level (1-5).
        deadline (datetime): The deadline for the task.
        suggestions (str): Suggestions for completing the task.
        
    Returns:
        str: A message indicating success or failure.
    """
    session = SessionLocal()
    try:
        new_task = Task(
            title=title,
            description=description,
            assign_by=assign_by,
            assignee=assignee_id,
            importance=str(importance),
            priority=str(priority),
            deadline=deadline,
            suggestions=suggestions,
            status="open",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(new_task)
        session.commit()
        return f"Task '{title}' created successfully for assignee {assignee_id}."
    except Exception as e:
        session.rollback()
        return f"Error creating task: {e}"
    finally:
        session.close()

def get_all_tasks():
    """
    Retrieves all tasks from the database.
    """
    session = SessionLocal()
    try:
        tasks = session.query(Task).all()
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assign_by": task.assign_by,
                "assignee": task.assignee,
                "importance": task.importance,
                "priority": task.priority,
                "deadline": task.deadline.strftime("%Y-%m-%d %H:%M:%S") if task.deadline else None,
                "suggestions": task.suggestions,
                "status": task.status,
                "created_at": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": task.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return task_list
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []
    finally:
        session.close()
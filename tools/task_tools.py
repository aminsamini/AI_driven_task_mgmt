from database.connection import SessionLocal
from database.models import User, Task
from datetime import datetime
from sqlalchemy.orm import aliased

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
        # Alias for assignee and assigner
        Assignee = aliased(User)
        Assigner = aliased(User)

        # Perform joins to get both assignee and assigner names
        results = session.query(Task, Assignee, Assigner)\
            .outerjoin(Assignee, Task.assignee == Assignee.id)\
            .outerjoin(Assigner, Task.assign_by == Assigner.id)\
            .all()
        
        task_list = []
        for task, assignee, assigner in results:
            assignee_name = "Unassigned"
            if assignee:
                assignee_name = f"{assignee.first_name} {assignee.last_name}"
            elif task.assignee:
                assignee_name = task.assignee

            assign_by_name = "Unknown"
            if assigner:
                assign_by_name = f"{assigner.first_name} {assigner.last_name}"
            elif task.assign_by:
                assign_by_name = task.assign_by

            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assign_by": task.assign_by,
                "assign_by_name": assign_by_name,
                "assignee": task.assignee,
                "assignee_name": assignee_name,
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

def update_task_status(task_id, new_status):
    """
    Updates the status of a task.
    """
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False, "Task not found"
        
        task.status = new_status
        task.updated_at = datetime.utcnow()
        session.commit()
        return True, "Status updated successfully"
    except Exception as e:
        session.rollback()
        return False, str(e)
    finally:
        session.close()
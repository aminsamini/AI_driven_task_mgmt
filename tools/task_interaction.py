from database.connection import SessionLocal
from database.models import Task
import cli
from datetime import datetime

def list_tasks(user_id):
    """
    Retrieves and displays tasks for the given user.
    Returns the list of tasks to allow selection.
    """
    session = SessionLocal()
    try:
        tasks = session.query(Task).filter(Task.assignee == user_id).all()
        
        if not tasks:
            cli.print_output("\nYou have no tasks assigned.")
            return []

        cli.print_output("\nYour Tasks:")
        for i, task in enumerate(tasks, 1):
            cli.print_output(f"{i}. {task.title} [{task.status}]")
        
        cli.print_output("\n0. Back to main menu")
        return tasks
    finally:
        session.close()

def show_task_details(task_id):
    """
    Displays details for a specific task.
    Returns the task object (detached) or None if not found.
    """
    session = SessionLocal()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if task:
            cli.print_output(f"\nTask Details:")
            cli.print_output(f"Title: {task.title}")
            cli.print_output(f"Description: {task.description}")
            cli.print_output(f"Status: {task.status}")
            cli.print_output(f"Priority: {task.priority}")
            cli.print_output(f"Importance: {task.importance}")
            cli.print_output(f"Deadline: {task.deadline}")
            cli.print_output(f"Created: {task.created_at}")
            cli.print_output(f"Suggestions: {task.suggestions}")
            
            # Return a dict representation to avoid detached instance errors if used later
            return {
                "id": task.id,
                "title": task.title,
                "status": task.status
            }
        else:
            cli.print_output("Task not found.")
            return None
    finally:
        session.close()

def change_task_status(task_id, current_status):
    """
    Allows the user to change the status of a task.
    """
    all_statuses = ["open", "in_progress", "paused", "finished", "closed"]
    available_statuses = [s for s in all_statuses if s != current_status]
    
    cli.print_output(f"\nCurrent Status: {current_status}")
    cli.print_output("Select new status:")
    
    for i, status in enumerate(available_statuses, 1):
        cli.print_output(f"{i}. {status}")
    
    cli.print_output("\n0. Cancel")
    
    while True:
        choice = cli.get_user_input("Select a status: ")
        if choice == '0':
            return False
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(available_statuses):
                new_status = available_statuses[index]
                
                session = SessionLocal()
                try:
                    task = session.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task.status = new_status
                        task.updated_at = datetime.utcnow()
                        session.commit()
                        cli.print_output(f"\n✅ Status updated to '{new_status}'.")
                        return True
                    else:
                        cli.print_output("Error: Task not found during update.")
                        return False
                except Exception as e:
                    session.rollback()
                    cli.print_output(f"Error updating status: {e}")
                    return False
                finally:
                    session.close()
            else:
                cli.print_output("Invalid selection. Please try again.")
        except ValueError:
            cli.print_output("Please enter a number.")

def handle_show_my_tasks(user_id):
    """
    Main handler for the /show_my_tasks command.
    """
    while True:
        tasks = list_tasks(user_id)
        if not tasks:
            # If no tasks, wait for user to acknowledge or just return
            if cli.get_user_input("Press Enter to return to main menu...") is not None:
                return

        choice = cli.get_user_input("\nSelect a task number: ")
        
        if choice == '0':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(tasks):
                selected_task = tasks[index]
                
                while True:
                    # Refresh task details view
                    task_data = show_task_details(selected_task.id)
                    if not task_data:
                        break # Task might have been deleted
                    
                    cli.print_output("\nActions:")
                    cli.print_output("1. Change Status")
                    cli.print_output("0. Back to task list")
                    
                    action = cli.get_user_input("Select an action: ")
                    
                    if action == '0':
                        break
                    elif action == '1':
                        if change_task_status(task_data['id'], task_data['status']):
                            # Status changed, loop will refresh details
                            pass
                    else:
                        cli.print_output("Invalid action.")
            else:
                cli.print_output("Invalid selection. Please try again.")
        except ValueError:
            cli.print_output("Please enter a number.")

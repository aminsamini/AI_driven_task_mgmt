import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock cli module BEFORE importing tools.task_interaction
sys.modules['cli'] = MagicMock()

from tools.task_interaction import list_tasks, show_task_details, change_task_status, handle_show_my_tasks
from database.models import Task
from datetime import datetime

class TestTaskInteraction(unittest.TestCase):

    @patch('tools.task_interaction.SessionLocal')
    def test_list_tasks(self, mock_session_cls):
        # Setup mock session and tasks
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        task1 = Task(id=1, title="Task 1", status="open", assignee="user1")
        task2 = Task(id=2, title="Task 2", status="in_progress", assignee="user1")
        mock_session.query.return_value.filter.return_value.all.return_value = [task1, task2]
        
        # Run function
        tasks = list_tasks("user1")
        
        # Verify
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0].title, "Task 1")
        # Check if print was called (via the mocked cli module)
        self.assertTrue(sys.modules['cli'].print_output.call_count >= 3)

    @patch('tools.task_interaction.SessionLocal')
    def test_show_task_details(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        task = Task(id=1, title="Task 1", description="Desc", status="open", 
                   priority="5", importance="5", deadline=datetime.now(), 
                   created_at=datetime.now(), suggestions="None")
        mock_session.query.return_value.filter.return_value.first.return_value = task
        
        result = show_task_details(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], "Task 1")
        self.assertTrue(sys.modules['cli'].print_output.call_count >= 8)

    @patch('tools.task_interaction.SessionLocal')
    def test_change_task_status(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session
        
        task = Task(id=1, title="Task 1", status="open")
        mock_session.query.return_value.filter.return_value.first.return_value = task
        
        # Simulate user selecting "in_progress" (option 1)
        sys.modules['cli'].get_user_input.return_value = "1" 
        
        result = change_task_status(1, "open")
        
        self.assertTrue(result)
        self.assertEqual(task.status, "in_progress")
        mock_session.commit.assert_called_once()

    @patch('tools.task_interaction.list_tasks')
    @patch('tools.task_interaction.show_task_details')
    @patch('tools.task_interaction.change_task_status')
    def test_handle_show_my_tasks_flow(self, mock_change, mock_details, mock_list):
        # Simulate flow
        task = MagicMock()
        task.id = 1
        mock_list.return_value = [task]
        
        mock_details.return_value = {'id': 1, 'status': 'open'}
        mock_change.return_value = True
        
        # Inputs: '1' (select task), '1' (change status), '0' (back to list), '0' (back to main)
        sys.modules['cli'].get_user_input.side_effect = ['1', '1', '0', '0']
        
        handle_show_my_tasks("user1")
        
        self.assertEqual(mock_list.call_count, 2)
        self.assertEqual(mock_details.call_count, 2)
        mock_change.assert_called_once()

if __name__ == '__main__':
    unittest.main()

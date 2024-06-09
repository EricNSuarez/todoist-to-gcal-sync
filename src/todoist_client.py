import logging
from typing import List, Optional
from todoist_api_python.api import TodoistAPI, Task
from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='sync.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_todoist_api() -> TodoistAPI:
    """
    Initializes and returns the Todoist API client.

    Returns:
        TodoistAPI: Authenticated Todoist API client instance.
    
    Raises:
        Exception: If an error occurs while initializing the Todoist API client.
    """
    try:
        api = TodoistAPI(Config.TODOIST_API_KEY)
        logging.info("Todoist API client initialized successfully.")
        return api
    except Exception as e:
        logging.error(f"An error occurred while initializing Todoist API client: {e}")
        raise

def get_tasks(
    api: TodoistAPI, 
    project_id: Optional[str] = None, 
    label_ids: Optional[List[str]] = None, 
    exclude_recurring: bool = False, 
    exclude_subtasks: bool = False
) -> List[Task]:
    """
    Retrieves tasks from Todoist, optionally filtered by project or labels.
    
    Parameters:
        api (TodoistAPI): Authenticated Todoist API client instance.
        project_id (Optional[str]): ID of the project to filter tasks.
        label_ids (Optional[List[str]]): List of label IDs to filter tasks.
        exclude_recurring (bool): If True, exclude recurring tasks.
        exclude_subtasks (bool): If True, exclude subtasks.
    
    Returns:
        List[Task]: List of tasks.
    
    Raises:
        Exception: If an error occurs while retrieving tasks from Todoist.
    """
    filters = None
    if exclude_recurring:
        filters = f"{filters} & !recurring" if filters else "!recurring"
    if exclude_subtasks:
        filters = f"{filters} & !subtask" if filters else filters
    
    try:
        tasks = api.get_tasks(project_id=project_id, label_ids=label_ids, filter=filters)
        logging.info(f"Retrieved {len(tasks)} tasks from Todoist.")
        return tasks
    except Exception as e:
        logging.error(f"An error occurred while retrieving tasks from Todoist: {e}")
        raise

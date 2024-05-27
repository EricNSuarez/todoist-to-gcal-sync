import logging
from todoist_api_python.api import TodoistAPI
from config.settings import Config

# Configure logging
logging.basicConfig(level=logging.INFO, filename='sync.log', filemode='a',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_todoist_api():
    """
    Initializes and returns the Todoist API client.
    """
    try:
        api = TodoistAPI(Config.TODOIST_API_KEY)
        logging.info("Todoist API client initialized successfully.")
        return api
    except Exception as e:
        logging.error(f"An error occurred while initializing Todoist API client: {e}")
        raise

def get_tasks(api, project_id=None, label_ids=None, exclude_recurring=False, exclude_subtasks=False):
    """
    Retrieves tasks from Todoist, optionally filtered by project or labels.
    
    :param api: Authenticated Todoist API client instance.
    :param project_id: (Optional) ID of the project to filter tasks.
    :param label_ids: (Optional) List of label IDs to filter tasks.
    :param exclude_recurring: (Optional) If you want to get recurring tasks.
    :return: List of tasks.
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


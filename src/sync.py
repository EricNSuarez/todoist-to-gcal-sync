import logging
import re
from src.gcal_client import create_gcal_service, add_reminder, create_calendar, sync_event
from src.todoist_client import get_todoist_api, get_tasks
from datetime import datetime, timedelta
from typing import Optional
from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename='sync.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def extract_duration(task_summary: str) -> Optional[int]:
    """
    Extracts the duration from the task summary.
    Duration can be specified in minutes or hours inside brackets [].
    Examples: "Task [30]" means 30 minutes, "Task [2h]" means 2 hours.

    Parameters:
        task_summary (str): The summary of the task.
    
    Returns:
        Optional[int]: Duration in minutes as an integer if found, otherwise None.
    """
    duration = None
    # Regex to match duration in minutes or hours inside brackets
    match = re.search(r'\[(\d+)(h|hours|horas|hs)?\]', task_summary, re.IGNORECASE)
    
    if match:
        value = int(match.group(1))
        if match.group(2):
            # Convert hours to minutes if the duration is specified in hours
            duration = value * 60
        else:
            # Use the value as is if the duration is specified in minutes
            duration = value
            
    return duration


def sync_todoist_to_gcal(default_event_duration: int = 30) -> None:
    """
    Syncs Todoist tasks to Google Calendar.

    Parameters:
        default_event_duration (int): The default duration for tasks/events in minutes.
    """
    try:
        # Initialize services
        todoist_api = get_todoist_api()
        gcal_service = create_gcal_service()
        
        # Ensure the calendar exists
        calendar_name = "Todoist Tasks"
        calendar = create_calendar(gcal_service, calendar_name)
        
        # Get tasks from Todoist, excluding subtasks and recurring tasks
        tasks = get_tasks(todoist_api, exclude_recurring=True, exclude_subtasks=True)
        
        # Sync tasks to Google Calendar
        for task in tasks:
            if not task.due or not task.due.date:
                continue  # Skip tasks without a due date
            
            due_date = task.due.date
            start_time = '09:00:00'
            if task.due.datetime:
                start_time = datetime.fromisoformat(task.due.datetime).time().isoformat()
            
            start_datetime = datetime.fromisoformat(due_date + 'T' + start_time)

            # Extract duration from task properties, task content, or set as default
            duration = extract_duration(task.content)
            if task.duration and task.duration.unit == 'minute':
                duration = task.duration.amount
            if duration is None:
                duration = default_event_duration
            
            end_datetime = start_datetime + timedelta(minutes=duration)

            timezone = task.due.timezone or Config.TIME_ZONE

            event = {
                'summary': task.content,
                'description': task.description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': timezone,
                },
            }
            event_with_reminder = add_reminder(event, 'popup', 15)
            created_event = sync_event(gcal_service, calendar['id'], event_with_reminder)
            print(f"Created or existing event: {created_event['htmlLink']}")
        
        logging.info("Sync completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during sync: {e}")
        raise

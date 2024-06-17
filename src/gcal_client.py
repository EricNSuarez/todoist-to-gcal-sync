import logging
import re
from dateutil.parser import parse
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from src.authentication import get_google_credentials
from config.settings import Config
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="sync.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

pattern = re.compile(
    r'\[(\d+)\s*(hours?|hrs?|h|horas?|hora|mins?|minutes?|min|m|minutos?)?\s*(\d+)?\s*(mins?|minutes?|min|m|minutos?)?\]',
    re.IGNORECASE
)

def remove_duration_pattern(summary: str) -> str:
    """
    Remove the duration pattern from the summary.
    
    Parameters:
        summary (str): The task summary from which the duration pattern needs to be removed.
    
    Returns:
        str: The summary with the duration pattern removed.
    """
    
    return re.sub(' +', ' ', pattern.sub(' ', summary)).strip()


def summaries_are_identical(summary1: str, summary2: str) -> bool:
    """
    Compare two summaries excluding the duration pattern.
    
    Parameters:
        summary1 (str): The first task summary.
        summary2 (str): The second task summary.
        
    Returns:
        bool: True if the summaries are identical excluding the duration pattern, False otherwise.
    """
    cleaned_summary1 = remove_duration_pattern(summary1)
    cleaned_summary2 = remove_duration_pattern(summary2)
    return cleaned_summary1 == cleaned_summary2


def create_gcal_service() -> Resource:
    """
    Creates and returns the Google Calendar API service.

    This function uses the credentials obtained from `get_google_credentials` to create
    an instance of the Google Calendar API service. If there is an error during the creation 
    of the service, it logs the error and raises an exception.

    Returns:
        Resource: An instance of the Google Calendar API service.

    Raises:
        HttpError: If an error occurs while creating the Google Calendar service.
    """
    credentials = get_google_credentials()
    
    if not credentials:
        logging.error("Failed to obtain Google credentials.")
        raise ValueError("Google credentials are not available.")

    try:
        # Build the Google Calendar service using the obtained credentials
        service = build("calendar", "v3", credentials=credentials)
        logging.info("Google Calendar service created successfully.")
        return service
    except HttpError as error:
        logging.error(f"An error occurred while creating Google Calendar service: {error}")
        raise


def create_event(service: Resource, calendar_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates an event in Google Calendar.

    Parameters
        service (Resource): Authenticated Google Calendar API service instance.
        calendar_id (str): ID of the calendar where the event will be created.
        event (Dict[str, Any]): Dictionary containing event details.

    Returns:
        Dict[str, Any]: The created event as a dictionary.

    Raises:
        HttpError: If an error occurs while creating the event.
    """
    try:
        # Create the event
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logging.info(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        logging.error(f"An error occurred while creating an event: {error}")
        raise


def update_event(service: Resource, calendar_id: str, event_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing event in Google Calendar.
    
    Parameters:
        service (Resource): Authenticated Google Calendar API service instance.
        calendar_id (str): ID of the calendar where the event will be updated.
        event_id (str): ID of the event to update.
        event (Dict[str, Any]): Dictionary containing updated event details.
    
    Return:
        Dict[str, Any]: The updated event.

    Raises:
        HttpError: If an error occurs while creating the event.
    """
    try:
        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        logging.info(f"Event updated: {updated_event.get('htmlLink')}")
        return updated_event
    except HttpError as error:
        logging.error(f"An error occurred while updating an event: {error}")
        raise


def sync_event(service: Resource, calendar_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Syncs an event by either creating a new event or updating an existing one if necessary. 
    
    Parameters:
        service (Resource): Authenticated Google Calendar API service instance.
        calendar_id (str): ID of the calendar where the event will be created or updated.
        event (Dict[str, Any]): Dictionary containing event details.
    
    Return:
        Dict[str, Any]: The created, already existing or updated event.

    Raise:
        HttpError: If an error occurs while creating the event.
    """
    try:
        new_start = parse(event['start']['dateTime']).replace(tzinfo=None)
        new_end = parse(event['end']['dateTime']).replace(tzinfo=None)
        existing_events = service.events().list(calendarId=calendar_id).execute().get('items', [])
        for existing_event in existing_events:
            summary_match  = summaries_are_identical(existing_event['summary'], event['summary'])
            if summary_match:
                timezones_match = (
                    existing_event['start']['timeZone'] == event['start']['timeZone'] and 
                    existing_event['end']['timeZone'] == event['end']['timeZone']
                )
                existing_start = parse(existing_event['start']['dateTime'])
                existing_end = parse(existing_event['end']['dateTime'])
                
                if (existing_start == new_start) and (existing_end == new_end) and timezones_match:
                    logging.info(f"Duplicate event detected: {existing_event.get('htmlLink')}")
                    return existing_event
                else:
                    # Update the event if the start, end datetime or timezone has changed
                    updated_event = update_event(service, calendar_id, existing_event['id'], event)
                    logging.info(f"Event updated: {updated_event.get('htmlLink')}")
                    return updated_event

        # Create new event if there are no matches with existing events
        created_event = create_event(service, calendar_id, event)
        logging.info(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        logging.error(f"An error occurred while syncing an event: {error}")
        raise


def add_reminder(event: Dict[str, Any], method: str = "popup", minutes_before_start: int = 10) -> Dict[str, Any]:
    """
    Adds a reminder to the event.

    Parameters:
        event (Dict[str, Any]): Dictionary containing event details.
        method (str): Method of reminder ('email', 'popup').
        minutes_before_start (int): Minutes before the event start to trigger the reminder.
    
    Returns:
        Dict[str, Any]: Updated event dictionary with reminder.
    """
    reminder = {
        "useDefault": False,
        "overrides": [
            {"method": method, "minutes": minutes_before_start},
        ],
    }
    event["reminders"] = reminder
    return event


def create_calendar(service: Resource, calendar_name: str) -> Dict[str, Any]:
    """
    Creates a new Google Calendar with the given name, ensuring it's not a duplicate.
    
    Parameters:
        service (Resource): Authenticated Google Calendar API service instance.
        calendar_name (str): The name of the calendar to be created.
    
    Returns:
        Dict[str, Any]: The created calendar or the existing calendar with the same name.
    
    Raises:
        HttpError: If an error occurs while creating the calendar.
    """
    try:
        # Check if the calendar already exists
        calendar_list = service.calendarList().list().execute()
        for calendar_entry in calendar_list['items']:
            if calendar_entry['summary'] == calendar_name:
                logging.info(f"Calendar '{calendar_name}' already exists.")
                return calendar_entry
        
        # Create a new calendar if not found
        calendar = {
            'summary': calendar_name,
            'timeZone': Config.TIME_ZONE
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        logging.info(f"Calendar created: {created_calendar['summary']}")
        return created_calendar
    except HttpError as error:
        logging.error(f"An error occurred while creating a calendar: {error}")
        raise

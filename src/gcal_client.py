import logging
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
    Creates an event in Google Calendar, avoiding duplicate events.

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
        # Check if the event already exists to avoid duplicates
        existing_events = service.events().list(calendarId=calendar_id).execute().get('items', [])
        for existing_event in existing_events:
            valid_summary = existing_event['summary'] == event['summary']
            valid_start_datetime = parse(event['start']['dateTime']) == parse(existing_event['start']['dateTime']).replace(tzinfo=None)
            valid_end_datetime = parse(event['end']['dateTime']) == parse(existing_event['end']['dateTime']).replace(tzinfo=None)
            valid_tzones = (
                existing_event['start']['timeZone'] == event['start']['timeZone'] and 
                existing_event['end']['timeZone'] == event['end']['timeZone']
            )

            if valid_summary and valid_start_datetime and valid_end_datetime and valid_tzones:
                logging.info(f"Duplicate event detected: {existing_event.get('htmlLink')}")
                return existing_event

        # Create the event if no duplicates are found
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logging.info(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        logging.error(f"An error occurred while creating an event: {error}")
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

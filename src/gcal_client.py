from google.auth.transport.requests import Request

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from src.authentication import get_google_credentials

from dateutil.parser import parse
import logging

from config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="sync.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def create_gcal_service():
    """
    Creates and returns the Google Calendar API service.
    """
    credentials = get_google_credentials()
    try:
        service = build("calendar", "v3", credentials=credentials)
        logging.info("Google Calendar service created successfully.")
        return service
    except HttpError as error:
        logging.error(
            f"An error occurred while creating Google Calendar service: {error}"
        )
        raise


def create_event(service, calendar_id, event):
    """
    Creates an event in Google Calendar, avoiding duplicate events.
    
    :param service: Authenticated Google Calendar API service instance.
    :param calendar_id: ID of the calendar where the event will be created.
    :param event: Dictionary containing event details.
    :return: The created event.
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

            if (
                valid_summary and
                valid_start_datetime and
                valid_end_datetime and 
                valid_tzones
            ):
                logging.info(f"Duplicate event detected: {existing_event.get('htmlLink')}")
                return existing_event

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        logging.info(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        logging.error(f"An error occurred while creating an event: {error}")
        raise


def add_reminder(event, method="popup", minutes_before_start=10):
    """
    Adds a reminder to the event.

    :param event: Dictionary containing event details.
    :param method: Method of reminder ('email', 'popup').
    :param minutes_before_start: Minutes before the event start to trigger the reminder.
    :return: Updated event dictionary with reminder.
    """
    reminder = {
        "useDefault": False,
        "overrides": [
            {"method": method, "minutes": minutes_before_start},
        ],
    }
    event["reminders"] = reminder
    return event


def create_calendar(service, calendar_name):
    """
    Creates a new Google Calendar with the given name, ensuring it's not a duplicate.
    
    :param service: Authenticated Google Calendar API service instance.
    :param calendar_name: The name of the calendar to be created.
    :return: The created calendar or the existing calendar with the same name.
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
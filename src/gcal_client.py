from google.auth.transport.requests import Request

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from src.authentication import get_google_credentials
import logging

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
    Creates an event in Google Calendar.

    :param service: Authenticated Google Calendar API service instance.
    :param calendar_id: ID of the calendar where the event will be created.
    :param event: Dictionary containing event details.
    :return: The created event.
    """
    try:
        created_event = (
            service.events().insert(calendarId=calendar_id, body=event).execute()
        )
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

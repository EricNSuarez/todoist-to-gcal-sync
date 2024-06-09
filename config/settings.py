import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class Config:
    """
    Configuration class for the application.

    Attributes:
        TODOIST_API_KEY (str): Todoist API key retrieved from environment variables.
        TIME_ZONE (str): Time zone retrieved from environment variables.
        SCOPES (list): List of Google Calendar API scopes.
    """

    # Load environment variables from a .env file if present
    load_dotenv()

    TODOIST_API_KEY: str = os.getenv("TODOIST_API_KEY")
    TIME_ZONE: str = os.getenv("TIME_ZONE")

    try:
        # Validate the provided time zone
        ZoneInfo(TIME_ZONE)
    except ZoneInfoNotFoundError:
        raise EnvironmentError(f"Invalid timezone: {TIME_ZONE}")

    SCOPES: list = [
        "https://www.googleapis.com/auth/calendar.app.created",
        "https://www.googleapis.com/auth/calendar.events.owned",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.calendarlist"
    ]

    @staticmethod
    def validate() -> None:
        """
        Validates the presence of necessary environment variables.
        Raises an exception if any required variable is missing.
        """
        missing_vars = [
            var
            for var in [
                "TODOIST_API_KEY",
                "TIME_ZONE"
            ]
            if not os.getenv(var)
        ]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

# Validate configuration
Config.validate()

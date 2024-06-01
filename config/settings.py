import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Load environment variables from a .env file if present
load_dotenv()


class Config:
    # Retrieve Todoist API key from environment variables
    TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
    TIME_ZONE = os.getenv("TIME_ZONE")

    try:
        ZoneInfo(TIME_ZONE)
    except ZoneInfoNotFoundError:
        raise EnvironmentError(f"Invalid timezone: {TIME_ZONE}")

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.app.created",
        "https://www.googleapis.com/auth/calendar.events.owned",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.calendarlist"
    ]

    @staticmethod
    def validate():
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

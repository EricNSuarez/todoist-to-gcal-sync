import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class Config:
    # Retrieve Todoist API key from environment variables
    TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")

    # Retrieve Google Calendar API credentials from environment variables
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")

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
                "GOOGLE_CLIENT_ID",
                "GOOGLE_CLIENT_SECRET",
                "GOOGLE_REFRESH_TOKEN",
            ]
            if not os.getenv(var)
        ]
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )


# Validate configuration
Config.validate()

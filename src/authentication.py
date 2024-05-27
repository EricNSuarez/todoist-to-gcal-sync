from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from config.settings import Config
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="sync.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def get_todoist_headers():
    """
    Returns the headers required for Todoist API requests.
    """
    headers = {"Authorization": f"Bearer {Config.TODOIST_API_KEY}"}
    return headers


def get_google_credentials():
    """
    Returns Google API credentials and handles token refresh if needed.
    """
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", Config.SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            # Refresh the token if expired
            try:
                credentials.refresh(Request())
                logging.info("Google credentials refreshed successfully.")
            except Exception as e:
                logging.error(f"Error refreshing Google credentials: {e}")
                raise
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", Config.SCOPES
            )
            credentials = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(credentials.to_json())

    return credentials

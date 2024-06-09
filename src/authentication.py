import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from config.settings import Config
from typing import Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    filename="sync.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def get_todoist_headers() -> Dict[str, str]:
    """
    Generate the headers required for Todoist API requests.

    Returns:
        Dict[str, str]: A dictionary containing the authorization header.
    """
    headers = {"Authorization": f"Bearer {Config.TODOIST_API_KEY}"}
    return headers

def get_google_credentials() -> Optional[Credentials]:
    """
    Retrieves Google API credentials, refreshing the token if necessary or initiating 
    an authorization flow if no valid credentials are found.

    This function checks for existing credentials in 'token.json'. If found and valid, 
    it returns them. If the credentials are expired and have a refresh token, it attempts 
    to refresh them. If no valid credentials are found, it initiates an OAuth2 flow to 
    obtain new credentials and saves them to 'token.json'.

    Returns:
        Optional[Credentials]: The Google API credentials or None if credentials are 
        not available or an error occurs during the refresh process.
    """
    credentials = None

    # Check if the token file exists and load credentials from it
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", Config.SCOPES)

    # If there are no valid credentials, refresh or initiate the OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                # Refresh the token if it has expired
                credentials.refresh(Request())
                logging.info("Google credentials refreshed successfully.")
            except RefreshError as e:
                logging.error(f"Error refreshing Google credentials: {e}")
                raise
        else:
            # Initiate the OAuth2 flow to obtain new credentials
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", Config.SCOPES)
            credentials = flow.run_local_server(port=0)
            # Save the new credentials to 'token.json'
            with open("token.json", "w") as token_file:
                token_file.write(credentials.to_json())

    return credentials

# Todoist to Google Calendar Synchronization Script

## Overview

This Python script synchronizes tasks from Todoist into Google Calendar, adding reminders to the calendar events. The script handles authentication for both Todoist and Google Calendar APIs by retrieving the relevant keys from environment variables, retrieves tasks from Todoist, creates corresponding events in Google Calendar, and sets reminders for these events.

## Features

- Synchronizes Todoist tasks to Google Calendar events.
- Adds customizable reminders to Google Calendar events.
- Filters tasks by project or label in Todoist.
- Securely handles authentication tokens and API requests.
- Logs relevant information and errors for troubleshooting purposes.

## Requirements

- Python 3.6 or higher
- Todoist API key
- Google Calendar API credentials

## Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/yourusername/todoist-to-gcal-sync.git
    cd todoist-to-gcal-sync
    ```

2. **Install Dependencies:**

    Use pip to install the required Python packages.

    ```bash
    pip install -r requirements.txt
    ```

3. **Set Environment Variables:**

    Create a `.env` file in the root directory of the project and add your Todoist and Google Calendar API credentials:

    ```
    TODOIST_API_KEY=your_todoist_api_key
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    GOOGLE_REFRESH_TOKEN=your_google_refresh_token
    ```

4. **Run the Script:**

    Execute the script to start synchronizing tasks from Todoist to Google Calendar.

    ```bash
    python sync_todoist_to_gcal.py
    ```

## Configuration

- **Filtering Tasks by Project or Label:**

    You can modify the script to filter tasks by specific projects or labels in Todoist. Update the `get_tasks` function to include your filtering logic.

- **Customizing Reminders:**

    The script provides default reminder settings. You can customize the reminder types (e.g., email, pop-up) and times (e.g., 10 minutes before, 1 hour before) in the `create_event_with_reminder` function.

## Logging

The script logs relevant information and errors to help with troubleshooting. Check the log file `sync.log` for details on the script's execution.

## Future Enhancements

- Improve performance for large task lists.
- Add support for synchronization with other task management or calendar systems.
- Provide a user-friendly configuration interface.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For questions or suggestions, please open an issue in the repository or contact the project maintainer at your-email@example.com.